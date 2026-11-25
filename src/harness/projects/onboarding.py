"""Describe how an existing research repository could be organized.

Used by project check for unfamiliar repositories and by the explicit
onboarding mode. The report reads the tree without executing project code.
"""

from pathlib import Path
import re


ENTRY_STEMS = {"train", "eval", "evaluate", "predict", "infer", "inference", "main", "run"}
ENTRY_SUFFIXES = {".py", ".sh", ".R", ".r", ".jl"}
CONFIG_SUFFIXES = {".yaml", ".yml", ".toml", ".json", ".ini", ".cfg"}
LOCATIONS = {
    "configs": ("Configuration", "conf/"),
    "config": ("Configuration", "conf/"),
    "conf": ("Configuration", "conf/"),
    "data": ("Data", "Keep source data in its current location and bind it when needed. Put loaders under datasets/."),
    "datasets": ("Datasets", "datasets/"),
    "models": ("Models", "models/"),
    "tasks": ("Tasks", "tasks/"),
    "checkpoints": ("Checkpoints", "Store run-generated checkpoints with their experiment artifacts. Document external weights with the model."),
    "outputs": ("Results", "Keep existing outputs and trace their run records before mapping them to experiment/."),
    "results": ("Results", "Keep existing outputs and trace their run records before mapping them to experiment/."),
    "experiment": ("Experiments", "experiment/"),
    "notebooks": ("Notebooks", "Keep exploratory notebooks with the analysis that uses them. Move reusable logic to its owning component."),
}


def entry_purpose(path):
    if not path.is_file() or path.is_symlink() or path.suffix not in ENTRY_SUFFIXES:
        return None
    stem = path.stem.lower()
    prefix = re.split(r"[_-]", stem, maxsplit=1)[0]
    if stem in ENTRY_STEMS or prefix in ENTRY_STEMS:
        return stem, prefix
    return None


def preview(project):
    """Return the observed paths and a bounded, read-only onboarding proposal."""
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Expected a project directory: {root}")
    entries, locations = [], []
    for path in sorted(root.iterdir()):
        if path.is_symlink():
            continue
        if role := entry_purpose(path):
            stem, prefix = role
            likely_variant = stem != prefix and (root / (prefix + path.suffix)).is_file()
            entries.append({
                "path": path.name,
                "suggestion": (
                    f"Possible variant of {prefix + path.suffix}. Compare callers and behavior before consolidating."
                    if likely_variant else
                    "Trace this entry point and preserve its current command."
                ),
            })
        if path.is_dir() and path.name in LOCATIONS:
            label, suggestion = LOCATIONS[path.name]
            children = sorted(p for p in path.iterdir() if not p.name.startswith(".") and not p.is_symlink())
            examples = children
            if label == "Configuration":
                examples = [p for p in children if p.is_file() and p.suffix.lower() in CONFIG_SUFFIXES]
            locations.append({
                "path": path.name + "/", "kind": label,
                "count": len(examples),
                "examples": [str(item.relative_to(root).as_posix()) for item in examples[:5]],
                "suggestion": suggestion,
            })
    return {
        "project": str(root),
        "mode": "onboarding",
        "entry_points": entries,
        "locations": locations,
        "next_step": (
            "Use EverResearch to plan onboarding this project. Trace its current commands, "
            "configuration, data, and existing outputs. Show the current and proposed paths, "
            "the behavior to preserve, and how you would verify it. Ask before editing any files."
        ),
    }


def format_preview(report):
    lines = [f"EverResearch onboarding preview for {report['project']}", "", "What I found"]
    for entry in report["entry_points"]:
        lines.append(f"  Entry point: {entry['path']}")
    for location in report["locations"]:
        examples = ", ".join(location["examples"])
        suffix = f" ({location['count']}{': ' + examples if examples else ''})"
        lines.append(f"  {location['kind']}: {location['path']}{suffix}")
    if not report["entry_points"] and not report["locations"]:
        lines.append("  Start with the project's README and documented commands.")
    lines.extend(("", "Proposed layout and checks"))
    for item in [*report["entry_points"], *report["locations"]]:
        lines.append(f"  {item['path']} -> {item['suggestion']}")
    if not report["entry_points"] and not report["locations"]:
        lines.append("  Map the entry points and existing outputs before proposing changes.")
    lines.extend(("", "Paste into your agent", f"  {report['next_step']}",
                  "", "Read-only preview. Review the plan before making changes."))
    return "\n".join(lines)


def format_check(report):
    if report["passed"]:
        summary = "Project check passed"
    else:
        summary = f"Project check found {len(report['violations'])} required fixes"
    lines = [f"{summary}: {report['project']}"]
    for item in report["violations"]:
        lines.append(f"  {item['path']}: {item['expected']}")
    if report["directory_reviews"]:
        lines.append("Advisory directory reviews")
        for item in report["directory_reviews"]:
            lines.append(f"  {item['path']}: {item['expected']}")
    return "\n".join(lines)
