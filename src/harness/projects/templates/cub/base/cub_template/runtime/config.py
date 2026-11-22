"""Purpose: Read and check classification configuration, parse equipment and data path.

Scope of application: All computing access points share the same parameters and environmental selection.
"""

from contextlib import contextmanager
from pathlib import Path
from threading import RLock
import tomllib

import torch
from hydra import compose, initialize_config_dir
from hydra.core.config_store import ConfigStore
from hydra.errors import HydraException
from omegaconf import OmegaConf
from omegaconf.errors import OmegaConfBaseException
from yaml import YAMLError


_COMPOSE_LOCK = RLock()
_CATALOGUE_GROUPS = ("dataset", "model", "task")


def register_catalogues(path):
    store = ConfigStore.instance()
    catalogs = OmegaConf.load(path).get("catalogs", {})
    for group in _CATALOGUE_GROUPS:
        for name, node in catalogs.get(group, {}).items():
            store.store(group=group, name=name, node=node, provider="cub_template")


@contextmanager
def isolated_catalogues(path):
    with _COMPOSE_LOCK:
        # Hydra uses a process-wide registry. Give this composition only its own
        # component presets, then put other projects' registrations back.
        store = ConfigStore.instance()
        original = {group: store.repo.pop(group, None) for group in _CATALOGUE_GROUPS}
        try:
            register_catalogues(path)
            yield
        finally:
            for group, previous in original.items():
                store.repo.pop(group, None)
                if previous is not None:
                    store.repo[group] = previous


def load(path, overrides=()):
    path = Path(path).resolve()
    if path.suffix in {".yaml", ".yml"}:
        directory = path.parent
        try:
            with (
                isolated_catalogues(path),
                initialize_config_dir(config_dir=str(directory), version_base="1.3"),
            ):
                config = OmegaConf.to_container(
                    compose(
                        config_name=path.stem,
                        overrides=list(overrides),
                    ),
                    resolve=True,
                )
        except (HydraException, OmegaConfBaseException, YAMLError) as exc:
            raise ValueError(f"Configuration group failed:{exc}") from exc
    else:
        if overrides:
            raise ValueError("Component Group Overwrite Usage YAML Formula")
        config = tomllib.loads(path.read_text(encoding="utf-8"))
    config.pop("catalogs", None)
    config.setdefault("task", {"name": "classification"})
    for section, key, minimum in [
        ("training", "seed", 0),
        ("runtime", "workers", 0),
        ("runtime", "cpu_threads", 1),
    ]:
        value = config[section][key]
        if type(value) is not int or value < minimum:
            raise ValueError(f"{section}.{key} It must be at least. {minimum} Integer number")
    if config["runtime"]["device"] not in {"auto", "cpu", "cuda"}:
        raise ValueError("runtime.device Please choose auto,cpu or cuda")
    return config


def resolve_data_root(config, config_path, override, *, requires_root):
    if not requires_root:
        if override is not None:
            raise ValueError("The selected data set is not accepted --data-root")
        return
    if override is not None:
        root = Path(override).expanduser()
    elif config.get("root"):
        root = Path(config_path).resolve().parent / config["root"]
    else:
        project = Path(__file__).resolve().parents[3]
        if project.parent.name == "templates" and (project.parents[4] / "src/harness/cli.py").is_file():
            project = project.parents[4]
        root = project.parent / "data/CUB_200/CUB_200_2011"
    config["root"] = str(root.resolve())


def prepare(config):
    runtime = config["runtime"]
    device = runtime["device"]
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA Not available, please prepare the corresponding environment or selection CPU")
    torch.set_num_threads(runtime["cpu_threads"])
    torch.manual_seed(config["training"]["seed"])
    runtime["device"] = device
    return torch.device(device)


def synchronize(device):
    if device.type == "cuda":
        torch.cuda.synchronize(device)
