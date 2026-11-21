"""Locate VGGT's generated files and validate names used in experiment paths."""

import os
import re
import uuid
from pathlib import Path


def project_root():
    root = Path(__file__).resolve().parents[2]
    return root if (root / "pyproject.toml").is_file() else None


def experiment_root():
    root = project_root()
    if root is not None:
        return root / "experiment"
    data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return data_home / "vggt" / "experiment"


def cache_root():
    cache_home = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return cache_home / "vggt"


def run_name(value):
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", value)
        or value in {"default", "experiment", "job", "output", "run", "test", "trial", "untitled"}
    ):
        raise ValueError(f"Invalid experiment name {value!r}. Describe its purpose in one to three words, such as camera_depth.")
    return value


def execution_id(timestamp):
    return f"{timestamp:%Y%m%dT%H%M%S.%fZ}-{uuid.uuid4().hex[:12]}"
