"""Read project defaults and expose the published Hydra recipe names."""
from importlib.resources import files
from pathlib import PurePosixPath

from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from .imports import source_root


def load_config(path="config.yaml"):
    root = source_root()
    resource = (root / "conf" if root else files("sam2").joinpath("recipes")).joinpath(path)
    with resource.open("r", encoding="utf-8") as stream:
        return OmegaConf.load(stream)


def register_recipes():
    store = ConfigStore.instance()
    for path in load_config().recipes:
        for name, config in load_config(path).items():
            location = PurePosixPath(name)
            store.store(
                group=location.parent.as_posix(),
                name=location.name,
                node=config,
                package="_global_",
                provider="sam2",
            )
            if location.parent.name == "sam2":
                store.store(name=location.name, node=config, provider="sam2")
