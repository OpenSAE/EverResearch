"""Track file state, structure findings, and maintenance notes for a project.

Used by the central maintenance command to report changes between checks.
The command reads the target project and writes its index in the local workspace.
"""

from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import stat
import sys

from harness.core import layout, naming, project
from harness.core.workspace import save, update_lock


def stamp(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns]


def inventory(root):
    """Enumerate visible paths without opening their contents."""
    entries = {}
    linked_directories = False
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as children:
            for child in children:
                if child.name.startswith(".") or child.name == "__pycache__":
                    continue
                path = Path(child.path)
                info = child.stat(follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    pending.append(path)
                entry = stamp(info)
                if stat.S_ISLNK(info.st_mode):
                    try:
                        target = child.stat()
                    except (FileNotFoundError, NotADirectoryError):
                        target = None
                    if target is not None:
                        entry += stamp(target)
                        linked_directories |= stat.S_ISDIR(target.st_mode)
                entries[path.relative_to(root).as_posix()] = entry
    return entries, linked_directories


def checker_version():
    modules = (layout, naming, project, sys.modules[project.read_record.__module__])
    return [
        1, list(sys.version_info[:3]), version("PyYAML"), version("pyspellchecker"),
        *[sha256(Path(module.__file__).read_bytes()).hexdigest() for module in modules],
    ]


def load_index(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def digest(entries):
    return sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


def check(harness, path, *, fresh=False, limit=20, record=None):
    root = harness.source_directory(path)
    if harness.root.is_relative_to(root):
        raise ValueError("The project catalogue must be separated from the central work")
    if limit < 1:
        raise ValueError("The number of summaries must be greater than zero")
    name = sha256(os.fsencode(root)).hexdigest()
    index = harness.resolve(f".workspace/harness/projects/maintenance/index_{name}.json")
    current_version = checker_version()
    with update_lock(index):
        previous = load_index(index)
        entries, linked_directories = inventory(root)
        previous_entries = previous.get("paths", {})
        old_facts = previous.get("facts", {})
        report = previous.get("project_check")
        same_rules = current_version == previous.get("checker")
        reused = (not fresh and not linked_directories and same_rules
                  and entries == previous_entries and isinstance(report, dict))
        facts = {}
        if same_rules and not fresh:
            for key, value in old_facts.items():
                relative = key.partition(":")[2]
                if relative in entries and entries[relative] == previous_entries.get(relative):
                    facts[key] = value

        def remember(file, inspect):
            relative = file.relative_to(root).as_posix()
            if relative not in entries:
                return inspect(file)
            key = f"{inspect.__name__}:{relative}"
            if key not in facts:
                facts[key] = inspect(file)
            return facts[key]

        checked_at = previous.get("checked_at")
        if not reused:
            report = project.check_project(root, remember=remember)
            if inventory(root) != (entries, linked_directories):
                raise ValueError("Changes in items during inspection, please recheck under current status")
            checked_at = datetime.now(timezone.utc).isoformat()

        changes = {
            "added": sorted(entries.keys() - previous_entries.keys()),
            "removed": sorted(previous_entries.keys() - entries.keys()),
            "modified": sorted(
                key for key in entries.keys() & previous_entries.keys()
                if entries[key] != previous_entries[key] and (
                    not stat.S_ISDIR(entries[key][2]) or entries[key][:3] != previous_entries[key][:3]
                )
            ),
        }
        maintenance = previous.get("maintenance")
        fingerprint = digest(entries)
        if record is not None:
            notes = json.loads(Path(record).read_text(encoding="utf-8"))
            if not isinstance(notes, dict) or set(notes) - {"entrypoints", "issues", "evidence"}:
                raise ValueError("Maintenance of records usage entrypoints,issues and evidence Fields")
            if any(not isinstance(items, list) for items in notes.values()):
                raise ValueError("The fields that maintain the records must be a list")
            maintenance = {"snapshot": fingerprint, "notes": notes}
        state = {
            "project": str(root), "checker": current_version, "paths": entries,
            "facts": facts, "project_check": report, "checked_at": checked_at,
            "maintenance": maintenance,
        }
        if state != previous:
            save(index, state, source=__file__)

    def summary(items):
        return {"count": len(items), "items": items[:limit]}

    return {
        "project": str(root), "index": str(index), "first_scan": not bool(previous),
        "changes": {key: summary(items) for key, items in changes.items()},
        "project_check": {
            "passed": report["passed"], "reused": reused, "checked_at": checked_at,
            "checked": report["checked"], "violations": summary(report["violations"]),
            "components": {key: summary(items) for key, items in report["components"].items()},
            "directory_reviews": summary(report["directory_reviews"]),
        },
        "maintenance": None if maintenance is None else {
            "project_changed": maintenance["snapshot"] != fingerprint,
            **{key: summary(items) for key, items in maintenance["notes"].items()},
        },
    }
