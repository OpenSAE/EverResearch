"""Save original project files before the first maintenance setup.

Used by setup-maintenance before it installs or removes project files.
"""

from io import BytesIO
import json
import os
from pathlib import Path
import stat
import tarfile
from tempfile import NamedTemporaryFile

from harness.core.workspace import update_lock


BACKUP_IGNORE = "/.researchharness/backups/"
LARGE_FILE_BYTES = 20 * 1024 * 1024
SKIP_DIRECTORIES = {"__pycache__", "node_modules", "venv", "virtualenv"}


def project_files(root):
    """Find visible project files without descending into caches or environments."""
    pending = [root]
    while pending:
        with os.scandir(pending.pop()) as children:
            for child in children:
                if child.name == ".git":
                    continue
                path = Path(child.path)
                info = child.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    yield path
                elif getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    continue
                elif stat.S_ISDIR(info.st_mode):
                    if (not child.name.startswith(".") and child.name not in SKIP_DIRECTORIES
                            and not (path / "pyvenv.cfg").is_file()
                            and not (path / "conda-meta").is_dir()):
                        pending.append(path)
                elif stat.S_ISREG(info.st_mode):
                    yield path


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

        setup_paths = set(paths)
        manifest = {"files": [], "links": {}, "created_paths": [], "large_files": []}
        location = None
        try:
            with NamedTemporaryFile(dir=directory, delete=False) as temporary:
                location = Path(temporary.name)
                with tarfile.open(fileobj=temporary, mode="w:gz") as bundle:
                    for path in sorted(setup_paths.union(project_files(root))):
                        if not path.parent.resolve().is_relative_to(root):
                            raise ValueError(f"Expected a setup path inside the project: {path}")
                        relative = path.relative_to(root).as_posix()
                        if path.is_symlink():
                            manifest["links"][relative] = str(path.readlink())
                        elif path.is_file():
                            size = path.stat().st_size
                            if path not in setup_paths and size > LARGE_FILE_BYTES:
                                manifest["large_files"].append({"path": relative, "size_bytes": size})
                            else:
                                bundle.add(path, arcname=f"files/{relative}", recursive=False)
                                manifest["files"].append(relative)
                        elif path.exists():
                            raise ValueError(f"Cannot back up a non-file setup path: {path}")
                        elif path in setup_paths:
                            manifest["created_paths"].append(relative)
                        else:
                            raise FileNotFoundError(f"Project file changed during the backup: {path}")
                    data = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
                    entry = tarfile.TarInfo("manifest.json")
                    entry.size = len(data)
                    bundle.addfile(entry, BytesIO(data))
            location.replace(archive)
        finally:
            if location is not None:
                location.unlink(missing_ok=True)
    return archive
