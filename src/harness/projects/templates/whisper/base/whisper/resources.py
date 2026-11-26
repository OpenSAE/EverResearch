"""Resolve bundled configuration and model resources in installed packages."""

from importlib.util import find_spec
from pathlib import Path


def resource_path(group: str, filename: str) -> Path:
    """Return a resource file from the package mapped to its source owner."""
    spec = find_spec(f"whisper.{group}")
    if spec is not None and spec.submodule_search_locations is not None:
        for location in spec.submodule_search_locations:
            candidate = Path(location) / filename
            if candidate.is_file():
                return candidate
    # Editable installs keep package data at its original location in the checkout.
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / "pyproject.toml").is_file():
        source_dirs = {
            "_configuration": checkout / "conf",
            "_resources": checkout / "assets" / "model_inputs" / "whisper" / "files",
        }
        candidate = source_dirs[group] / filename
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(f"Whisper resource is missing: {group}/{filename}")
