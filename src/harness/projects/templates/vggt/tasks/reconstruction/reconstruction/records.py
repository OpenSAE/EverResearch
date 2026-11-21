"""Store complete COLMAP bundles and restore their interoperable native filenames."""

import argparse
import json
from pathlib import Path
from zipfile import ZipFile


def pack_reconstruction(sparse, target):
    """Keep the native COLMAP filenames together inside one declared artifact."""
    with ZipFile(target, "x") as archive:
        for file in sorted(sparse.iterdir()):
            if file.is_file():
                archive.write(file, file.name)


def unpack_reconstruction(manifest, destination):
    """Restore the one-level native reconstruction beside its PLY point cloud."""
    manifest = Path(manifest)
    record = json.loads(manifest.read_text())
    bundle = manifest.parent.parent / record["outputs"]["reconstruction"]
    destination = Path(destination)
    with ZipFile(bundle) as archive:
        names = archive.namelist()
        if any(Path(name).name != name or name in {".", ".."} or "\\" in name for name in names):
            raise ValueError("The reconstruction archive must contain only native COLMAP files.")
        destination.mkdir(parents=True, exist_ok=False)
        for name in names:
            (destination / name).write_bytes(archive.read(name))
    return destination


def main():
    parser = argparse.ArgumentParser(description="Unpack a saved VGGT reconstruction for COLMAP")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(unpack_reconstruction(args.manifest, args.destination))
