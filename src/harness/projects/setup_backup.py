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
BACKUP_LOCK_IGNORE = "/.researchharness/.initial-setup.lock"
LARGE_FILE_BYTES = 20 * 1024 * 1024
BACKUP_BUDGET_BYTES = 200_000_000
SKIP_DIRECTORIES = {"__pycache__", "node_modules", "venv", "virtualenv"}
INVENTORY_SUFFIXES = set("""
    .npy .npz .pt .pth .ckpt .safetensors .bin .h5 .hdf5 .parquet .arrow .pkl .pickle
    .csv .tsv .jsonl .feather .orc .avro .sqlite .db .mat .gguf .onnx .tflite .keras
    .zip .tar .gz .tgz .bz2 .tbz2 .xz .txz .zst .rar .7z .lz4 .whl
    .png .jpg .jpeg .gif .webp .bmp .tif .tiff .svg .ico .heic .heif .avif .jfif .raw
    .wav .mp3 .flac .ogg .oga .m4a .aac .opus .aiff .wma
    .mp4 .m4v .mov .avi .mkv .webm .mpg .mpeg .wmv .flv .m4p
""".split())
PREFERRED_SUFFIXES = set("""
    .py .pyi .ipynb .r .jl .m .c .h .cc .cpp .hpp .cu .cuh .rs .go .java .kt
    .js .jsx .mjs .ts .tsx .sh .bash .zsh .ps1 .bat .sql .cmake
    .toml .yaml .yml .json .ini .cfg .conf .xml .lock
    .md .rst .txt .adoc .tex .bib .html .css .pdf
""".split())
PREFERRED_NAMES = {"makefile", "dockerfile", "license", "readme", "copying"}


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


def remove_legacy_backup_lock(root):
    """Remove the empty lock left by older setups after an archive exists."""
    directory = root / ".researchharness/backups"
    archive = directory / "initial-setup.tar.gz"
    lock = directory / "initial-setup.tar.lock"
    if directory.is_symlink() or not directory.resolve().is_relative_to(root):
        return
    if archive.is_symlink() or not archive.is_file() or lock.is_symlink():
        return
    try:
        info = lock.stat()
    except FileNotFoundError:
        return
    if stat.S_ISREG(info.st_mode) and info.st_size == 0:
        lock.unlink(missing_ok=True)


def save_initial_backup(root, paths):
    """Write a complete archive once and reuse it if setup needs to be retried."""
    directory = root / ".researchharness/backups"
    if directory.is_symlink() or not directory.resolve().is_relative_to(root):
        raise ValueError(f"Expected a backup directory inside the project: {directory}")
    archive = directory / "initial-setup.tar.gz"
    # Keep the stable lock inode outside the backup directory so waiting callers share it.
    with update_lock(directory.parent / ".initial-setup"):
        if archive.is_symlink() or (archive.exists() and not archive.is_file()):
            raise ValueError(f"Expected a regular backup file: {archive}")
        if archive.is_file():
            return archive

        setup_paths = set(paths)
        manifest = {"files": [], "links": {}, "created_paths": [], "large_files": []}
        directory.mkdir(exist_ok=True)
        remaining = BACKUP_BUDGET_BYTES
        location = None
        ordered = sorted(setup_paths.union(project_files(root)), key=lambda path: (
            path not in setup_paths,
            path.suffix.lower() not in PREFERRED_SUFFIXES and path.name.lower() not in PREFERRED_NAMES,
            path,
        ))
        try:
            with NamedTemporaryFile(dir=directory, delete=False) as temporary:
                location = Path(temporary.name)
                with tarfile.open(fileobj=temporary, mode="w:gz", dereference=True) as bundle:
                    for path in ordered:
                        if not path.parent.resolve().is_relative_to(root):
                            raise ValueError(f"Expected a setup path inside the project: {path}")
                        relative = path.relative_to(root).as_posix()
                        if path.is_symlink():
                            manifest["links"][relative] = str(path.readlink())
                        elif path.is_file():
                            size = path.stat().st_size
                            if path.suffix.lower() in INVENTORY_SUFFIXES or (
                                path not in setup_paths and size > min(LARGE_FILE_BYTES, remaining)
                            ):
                                manifest["large_files"].append({"path": relative, "size_bytes": size})
                            else:
                                if size > remaining:
                                    raise ValueError("Setup files exceed the initial backup limit of 200 MB.")
                                with path.open("rb") as stream:
                                    entry = bundle.gettarinfo(arcname=f"files/{relative}", fileobj=stream)
                                    if not entry.isfile() or entry.size != size:
                                        raise ValueError(f"Project file changed during the backup: {path}")
                                    bundle.addfile(entry, stream)
                                remaining -= size
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
