# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the Apache License, Version 2.0
# found in the LICENSE file in the root directory of this source tree.

from pathlib import Path

from omegaconf import OmegaConf
from dinov2.configs import bundled


_PRESET_GROUPS = {"train": "training", "eval": "classification"}


def load_config(config_name: str):
    """Load the original default or a named configuration shipped with DINOv2."""
    resources = Path(next(iter(bundled.__path__)))
    name = str(config_name).removesuffix(".yaml")
    if name in {"ssl_default_config", "config"}:
        return OmegaConf.load(resources.joinpath("config.yaml"))

    group, separator, preset = name.partition("/")
    if not separator or group not in _PRESET_GROUPS:
        raise FileNotFoundError(f"Unknown DINOv2 configuration: {config_name}")
    resource = resources.joinpath("tasks").joinpath(_PRESET_GROUPS[group]).joinpath("config.yaml")
    config = OmegaConf.load(resource)
    if preset not in config:
        raise FileNotFoundError(f"Unknown DINOv2 configuration: {config_name}")
    return OmegaConf.create(OmegaConf.to_container(config[preset], resolve=False))


def load_user_config(reference):
    """Resolve a user file, bundled preset, or previous bundled configuration path."""
    if reference is None:
        raise ValueError("Provide a DINOv2 configuration using --config-file.")
    path = Path(reference).expanduser()
    if path.is_file():
        return OmegaConf.load(path)
    name = path.as_posix()
    if "/dinov2/configs/" in name or name.startswith("dinov2/configs/"):
        name = name.rsplit("dinov2/configs/", maxsplit=1)[-1]
    return load_config(name)


dinov2_default_config = load_config("ssl_default_config")


def load_and_merge_config(config_name: str):
    default_config = OmegaConf.create(dinov2_default_config)
    return OmegaConf.merge(default_config, load_config(config_name))
