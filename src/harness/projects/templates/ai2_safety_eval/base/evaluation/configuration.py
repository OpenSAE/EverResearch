"""Read the installed project configuration and its task and classifier presets."""

from importlib.util import find_spec
from pathlib import Path

import yaml


def package_directory(name):
    spec = find_spec(name)
    if spec is not None:
        for location in spec.submodule_search_locations or ():
            path = Path(location)
            if path.is_dir():
                return path
    raise FileNotFoundError(f"Installed resource package {name!r} has no files.")


def load_configuration(path):
    resource = package_directory("ai2_safety_configuration").joinpath(path)
    return yaml.safe_load(resource.read_text(encoding="utf-8"))
