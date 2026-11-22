"""Resolve source workspace and default model resource locations."""
from pathlib import Path

from .imports import source_root


def project_workspace():
    root = source_root()
    if root is not None:
        return root
    for directory in (Path.cwd(), *Path.cwd().parents):
        if (directory / "conf" / "config.yaml").is_file() and (directory / "setup.py").is_file():
            return directory
    return None


def data_root():
    root = project_workspace() or Path.cwd()
    if root.parent.name == "templates" and (root.parents[4] / "src/harness/cli.py").is_file():
        root = root.parents[4]
    return root.parent / "data" / "sam2"


def checkpoint_path(filename):
    return data_root() / "checkpoints" / "local" / filename
