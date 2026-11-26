"""Resolve image and video inputs accepted by the upstream command-line workflows."""

from pathlib import Path


def media_files(path):
    path = Path(path)
    if path.is_dir():
        return sorted(item for item in path.rglob("*") if item.is_file() and not item.name.startswith("."))
    if path.suffix.lower() == ".txt":
        return [Path(line) for line in path.read_text().splitlines() if line.strip()]
    return [path]
