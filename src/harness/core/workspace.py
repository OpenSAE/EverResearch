"""Purpose and main function: provision of central JSON Atom Writing and Workspace Production Log.

Scope of application: Called by a central write-in entry and independent tool with a defined target path.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
import stat
import uuid
from pathlib import Path


def record_files(paths, *, source, summary):
    """Append one short event per artifact file to its third-level directory log."""
    grouped = {}
    for raw in paths:
        path = Path(raw).absolute()
        positions = [i for i, part in enumerate(path.parts) if part == ".workspace"]
        if not positions or not path.is_file() or path.is_symlink():
            continue
        position = positions[-1]
        relative = path.parts[position + 1 :]
        depth = 2 if relative[:1] == ("tmp",) else 3
        if len(relative) <= depth or path.name == "log_updates.jsonl":
            continue
        workspace = Path(*path.parts[: position + 1])
        bucket = workspace.joinpath(*relative[:depth])
        event = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "artifact": path.relative_to(bucket).as_posix(),
            "summary": summary,
            "source": source,
        }
        grouped.setdefault(bucket, []).append(event)
    for bucket, events in grouped.items():
        log = bucket / "log_updates.jsonl"
        if log.is_symlink():
            raise ValueError("Workspace log must not be a symlink")
        with log.open("a", encoding="utf-8") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            for event in events:
                stream.write(json.dumps(event, ensure_ascii=False) + "\n")
            stream.flush()
            fcntl.flock(stream, fcntl.LOCK_UN)


@contextmanager
def update_lock(path):
    """Serialize read-modify-write operations on a local binding file."""
    lock = path.with_suffix(".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def save_bytes(path, content, *, source="src/harness/core/workspace.py"):
    """Atomically preserve exact bytes for a result or a recoverable rollback."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        temporary.write_bytes(content)
        if path.exists():
            previous = path.stat()
            if os.geteuid() == 0:
                os.chown(temporary, previous.st_uid, previous.st_gid)
            temporary.chmod(stat.S_IMODE(previous.st_mode))
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    record_files([path], source=source, summary="Write artifact")


def save(path, value, *, source="src/harness/core/workspace.py"):
    content = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    save_bytes(path, content, source=source)
