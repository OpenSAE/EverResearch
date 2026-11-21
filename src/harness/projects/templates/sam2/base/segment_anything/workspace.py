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


def checkpoint_path(filename):
    root = project_workspace()
    return root / "data" / "checkpoints" / "local" / filename if root else Path("checkpoints") / filename
