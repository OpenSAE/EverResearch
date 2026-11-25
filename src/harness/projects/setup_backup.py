"""Save the original project files involved in the first maintenance setup.

Used by setup-maintenance before it installs or removes project files.
"""

from io import BytesIO
import json
from pathlib import Path
import tarfile
from tempfile import NamedTemporaryFile

from harness.core.workspace import update_lock


BACKUP_IGNORE = "/.researchharness/backups/"


def save_initial_backup(root, paths):
    """Write a complete archive once and reuse it if setup needs to be retried."""
    directory = root / ".researchharness/backups"
    if directory.is_symlink() or not directory.resolve().is_relative_to(root):
        raise ValueError(f"Expected a backup directory inside the project: {directory}")
    archive = directory / "initial-setup.tar.gz"
    with update_lock(archive):
        if archive.is_symlink() or (archive.exists() and not archive.is_file()):
            raise ValueError(f"Expected a regular backup file: {archive}")
        if archive.is_file():
            return archive

        manifest = {"files": [], "links": {}, "created_paths": []}
        location = None
        try:
            with NamedTemporaryFile(dir=directory, delete=False) as temporary:
                location = Path(temporary.name)
                with tarfile.open(fileobj=temporary, mode="w:gz") as bundle:
                    for path in sorted(set(paths)):
                        if not path.parent.resolve().is_relative_to(root):
                            raise ValueError(f"Expected a setup path inside the project: {path}")
                        relative = path.relative_to(root).as_posix()
                        if path.is_symlink():
                            manifest["links"][relative] = str(path.readlink())
                        elif path.is_file():
                            bundle.add(path, arcname=f"files/{relative}", recursive=False)
                            manifest["files"].append(relative)
                        elif path.exists():
                            raise ValueError(f"Cannot back up a non-file setup path: {path}")
                        else:
                            manifest["created_paths"].append(relative)
                    data = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
                    entry = tarfile.TarInfo("manifest.json")
                    entry.size = len(data)
                    bundle.addfile(entry, BytesIO(data))
            location.replace(archive)
        finally:
            if location is not None:
                location.unlink(missing_ok=True)
    return archive
