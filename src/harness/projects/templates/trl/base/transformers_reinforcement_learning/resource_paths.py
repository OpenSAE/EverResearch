"""Locate the packaged TRL assets used by trainers and command-line launchers.

The installed wheel stores the assets in the TRL package. Editable installs use
files from the corresponding project asset directories.
"""

from pathlib import Path


_SOURCE_ASSETS = {
    "accelerate_configs": Path("configuration/accelerate/files"),
    "chat_templates": Path("templates/chat/files"),
    "templates": Path("templates/cards/files"),
}


def resource_directory(name: str) -> Path:
    """Locate a shipped asset directory for the active installation."""
    package_root = Path(__file__).resolve().parent
    packaged = package_root / name
    if packaged.is_dir():
        return packaged
    return package_root.parents[1] / "assets" / _SOURCE_ASSETS[name]
