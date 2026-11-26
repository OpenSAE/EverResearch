"""Connect to central maintenance guidelines and distribution of project resources and structural results operations.

For defined selection of workspaces and projects rh projects Command.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tomllib

import yaml

from harness.central import HarnessContext, ProjectError, identity, installed_resources, load_harness
from harness.core.experiment import check_experiment
from harness.core.layout import check_layout
from harness.core.check import check_precheck
from harness.core.project import check_project

from . import onboarding
from harness.core.workspace import save, save_bytes, update_lock
from . import maintenance, resources, structure
from .setup_backup import BACKUP_IGNORE, BACKUP_LOCK_IGNORE, remove_legacy_backup_lock, save_initial_backup
from .standalone.maintain import online_guide as check_online_guide, require_file

START = "<!-- researchharness:projects -->"
END = "<!-- /researchharness:projects -->"
MODE_START = "<!-- researchharness:mode -->"
MODE_END = "<!-- /researchharness:mode -->"
SEARCH_START = "<!-- researchharness:search -->"
SEARCH_END = "<!-- /researchharness:search -->"
SEARCH_GUIDANCE = '## Locate projects and files\n\nStart with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.'
ONLINE_IGNORE = "/.researchharness/online/"
MAINTENANCE_SKILLS = {
    "maintain-project": "Project setup, inspection, and changes across components",
    "maintain-base": "Shared commands, resource selection, and component wiring",
    "maintain-dataset": "Data loading, preprocessing, splits, and caches",
    "maintain-model": "Model variants, initialization, and weights",
    "maintain-task": "Training, evaluation, prechecks, and metrics",
    "maintain-conf": "Configuration defaults, presets, and overrides",
    "maintain-experiment": "Experiment setup, execution, reproduction, and results",
    "maintain-optional": "Standalone scripts, tests, documentation, and assets",
    "maintain-code": "Code changes and their callers",
    "maintain-tmp": "Disposable files and one-off diagnostics",
    "maintain-skill": "Maintenance workflow review and updates",
    "maintain-knowledge": "Research notes and reusable findings",
}

PROJECT_ACTIONS = (
    ("Read and plan", "read", "Existing commands, configurations, and records"),
    ("Change a shared command", "base", "`base/` and existing entry points"),
    ("Change a dataset", "datasets", "`datasets/`"),
    ("Change a model", "models", "`models/`"),
    ("Change a task or precheck", "tasks", "`tasks/`"),
    ("Change a configuration", "conf", "`conf/`"),
    ("Run an experiment or read its results", "experiment", "Existing entry point and `experiment/`"),
    ("Add a test or standalone script", "tests-scripts", "`tests/`, `scripts/`, or the component it supports"),
    ("Create disposable work", "tmp", "`tmp/<purpose>/`"),
    ("Update the Python environment", "environment", "Project Python and `doc/environment/`"),
    ("Download and prepare data", "data", "Workspace `data/<dataset>/<version>/`"),
    ("Store reusable resources", "assets", "`assets/<type>/<resource>/` or the existing cache"),
    ("Maintain third-party code", "third-party", "`third_party/<upstream>/`"),
    ("Update documentation", "doc", "`doc/` and its navigation"),
)


def settings(harness, project_id):
    """Read the explicit user choice and check its existing project binding."""
    project_id = identity(project_id)
    path = harness.project_record(project_id, "project.yaml")
    root = harness.project_root(project_id)
    value = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {"skills": True}
    if (
        not isinstance(value, dict)
        or value.get("project_id", project_id) != project_id
        or type(value.get("skills")) is not bool
    ):
        raise ProjectError("Project Sharing Settings skills use true/false")
    lightweight_checks = value.get("lightweight_checks", False)
    if type(lightweight_checks) is not bool:
        raise ProjectError("Projects lightweight_checks Settings for use true/false")
    return path, root, {"skills": value["skills"], "lightweight_checks": lightweight_checks}


def updated_settings(path, project_id, changes):
    """Preserve ordinary settings files and keep valid YAML mappings readable."""
    if not path.exists():
        return (
            "# Purpose and main function: Preservation of project identifiers, shared skills and light validation options.\n"
            "# Scope of application: rh projects Query and Sync Project Access.\n"
            + yaml.safe_dump({"project_id": project_id, "skills": True, **changes}, sort_keys=False)
        )
    original = path.read_text(encoding="utf-8")
    expected = {**yaml.safe_load(original), **changes}
    text = original
    for key, enabled in changes.items():
        setting = f"{key}: {str(enabled).lower()}"
        text, count = re.subn(
            rf"^{re.escape(key)}:[^\n#]*(#[^\n]*)?",
            lambda match: f"{setting}  {match[1]}" if match[1] else setting,
            text, flags=re.M,
        )
        if not count:
            text = f"{text.rstrip()}\n{setting}\n"
    try:
        if yaml.safe_load(text) == expected:
            return text
    except yaml.YAMLError:
        pass
    return yaml.safe_dump(expected, sort_keys=False, allow_unicode=True)


def catalogue(harness):
    """Only expose maintained top-level skills, including each complete directory."""
    directory = harness.resolve(".agents/skills", exists=True)
    return {p.name: p for p in sorted(directory.iterdir()) if (p / "SKILL.md").is_file()}


def state_path(harness, project_id):
    return harness.resolve(f".workspace/harness/projects/manage/connection_{identity(project_id)}.json")


def project_maintenance_mode(root):
    """Read the explicit switch for projects that carry standalone maintenance."""
    directory = root / ".researchharness"
    path = directory / "mode.toml"
    if directory.is_symlink() or path.is_symlink():
        raise ProjectError("Project maintenance switches shall be a normal file within the project")
    if not path.exists():
        return None
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if set(data) != {"enabled"} or type(data["enabled"]) is not bool:
        raise ProjectError("Set enabled = true or enabled = false in .researchharness/mode.toml.")
    return data["enabled"]


def online_guide(harness, project_id):
    return harness.resolve(f".workspace/harness/projects/manage/guide_{identity(project_id)}.md")


def maintenance_guidance(skill_path, operations_path, desired, lightweight_checks):
    if not desired:
        return ""
    lines = [
        "### Daily maintenance and lightweight checks",
        "",
        "Start with the project command and the skill for the component you are changing. "
        "Use the operations manual to resolve ownership or coordinate changes across components.",
        "",
        "| Operation | Project location |",
        "| --- | --- |",
        *(f"| [{action}](<{operations_path.as_posix()}#{section}>) | {destination} |"
          for action, section, destination in PROJECT_ACTIONS),
    ]
    rows = [
        f"| {purpose} | [`{name}`]({(skill_path / name / 'SKILL.md').as_posix()}) |"
        for name, purpose in MAINTENANCE_SKILLS.items()
        if name in desired
    ]
    rows.extend(
        f"| Shared skills | [`{name}`]({(skill_path / name / 'SKILL.md').as_posix()}) |"
        for name in sorted(desired.keys() - MAINTENANCE_SKILLS.keys())
    )
    if rows:
        lines.extend(("", "| What you are maintaining | Skill to read |", "| --- | --- |", *rows))
    if lightweight_checks:
        lines.extend((
            "",
            "**Lightweight follow-up checks are enabled.** Run the smallest relevant check "
            "through the normal entry point. Use `rh projects layout check` for path changes "
            "and `rh projects project check --json` for the full project check. Run one "
            "structure check for each state of the project tree. Use `rh projects maintenance` "
            "when authorized to update the maintenance index.",
            "",
            "Use `rh projects experiment check` for run records and `rh projects precheck check` "
            "for precheck evidence. Start with existing small tests, configuration previews, or "
            "prechecks. Follow the task authorization for downloads, installation, and scientific runs.",
            "",
            "Report the command, behavior tested, observed result, and any evidence still needed.",
        ))
    else:
        lines.extend(("", "**Lightweight follow-up checks follow the task authorization.** When authorized, use central read-only checks and existing project checks."))
    return "\n\n" + "\n".join(lines)


def relative_or_absolute(path, directory):
    try:
        return Path(os.path.relpath(path, directory))
    except ValueError:
        return path


def guidance(harness, project_id, value, desired, guide):
    if not value["skills"]:
        return f"""{START}
## EverResearch project resources

Use this project's README to install dependencies, choose a configuration, and run the project.
Run `rh projects resources {project_id}` to see the Python interpreter and data paths bound on this machine.
{END}"""
    operations_path = relative_or_absolute(harness.root / "src/harness/projects/operations.md", guide.parent)
    skill_path = relative_or_absolute(harness.root / ".agents/skills", guide.parent)
    notes = harness.project_record(project_id) / "README.md"
    notes_path = relative_or_absolute(notes, guide.parent)
    workflow = maintenance_guidance(skill_path, operations_path, desired, value["lightweight_checks"])
    return f"""{START}
## EverResearch online maintenance

### Purpose and main function

Provides shared maintenance guidance and checks for the registered project `{project_id}`.

### Scope of application

Use this guide in online mode. Follow the project's README for installation, configuration, and public commands. Use the requested scope for changes and verification.

Run `rh projects resources {project_id}` to see the Python interpreter and data paths bound on this machine. Project-specific maintenance notes, when available, are at `{notes_path}`. The skill links below open the shared instructions.{workflow}
{END}"""


def agent_text(text, block):
    """Update only the owned section, preserving the project's other instructions."""
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ProjectError("AGENTS.md Incomplete project access paragraph tags")
    if START in text:
        before, rest = text.split(START, 1)
        _, after = rest.split(END, 1)
        return before + block + after
    return text.rstrip() + "\n\n" + block + "\n"


def with_search_guidance(text):
    """Write the same search instructions into every generated project guide."""
    if text.count(SEARCH_START) != text.count(SEARCH_END) or text.count(SEARCH_START) > 1:
        raise ProjectError("AGENTS.md in which the search paragraph tags are incomplete")
    block = f"{SEARCH_START}\n{SEARCH_GUIDANCE}\n{SEARCH_END}"
    if SEARCH_START in text:
        before, rest = text.split(SEARCH_START, 1)
        if SEARCH_END not in rest:
            raise ProjectError("AGENTS.md in which the search paragraph is marked in the wrong order")
        _, after = rest.split(SEARCH_END, 1)
        return before + block + after
    positions = [text.index(marker) for marker in (MODE_START, START) if marker in text]
    if positions:
        start = min(positions)
        return text[:start] + block + "\n\n" + text[start:]
    separator = "\n\n" if text.strip() else ""
    return text.rstrip() + separator + block + "\n"


def legacy_skill_changes(harness, root, installed):
    """Plan changes to central-generated aliases and guides."""
    known = catalogue(harness)
    previous = {name: harness.root / target for name, target in installed.get("links", {}).items()}
    changes = {}
    cleanup = set()
    for relative in (".agents/skills", ".agents/researchharness-skills",
                     ".researchharness/online/skills"):
        directory = root / relative
        if (directory.is_symlink() or not directory.resolve().is_relative_to(root)
                or not directory.is_dir()):
            continue
        for name in known.keys() | previous.keys():
            link = directory / name
            if link.is_symlink() and link.resolve() in {known.get(name), previous.get(name)}:
                changes[link] = None
                cleanup.add(directory)
        entry = directory / "researchharness/SKILL.md"
        if is_legacy_skill_guide(root, entry):
            changes[entry] = None
            cleanup.update((entry.parent, directory))

    entry = root / ".researchharness/legacy/connection_guide.md"
    if is_legacy_skill_guide(root, entry):
        changes[entry] = None
    guide = root / ".researchharness/online/README.md"
    if (guide.is_file() and not guide.is_symlink() and not guide.parent.is_symlink()
            and guide.resolve().is_relative_to(root)):
        original = guide.read_text(encoding="utf-8")
        if START in original:
            remaining = agent_text(original, "")
            changes[guide] = remaining.encode() if remaining.strip() else None
    return changes, cleanup


def remove_legacy_skill_files(harness, root, installed, *, plan=None):
    changes, cleanup = plan if plan is not None else legacy_skill_changes(harness, root, installed)
    for path, content in changes.items():
        if content is None:
            path.unlink()
        else:
            save_bytes(path, content, source=__file__)
    for directory in sorted(cleanup, key=lambda path: len(path.parts), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()


def is_legacy_skill_guide(root, path):
    if (path.is_symlink() or path.parent.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(root)):
        return False
    content = path.read_bytes()
    template = Path(__file__).with_name("researchharness.skill.md.in").read_bytes()
    # Recognize the previous distributed guide as well as the last template.
    older_guide = "e0adfe5c565832c410fc914bd4518d8878c594b82810f598d2a67751d57cdcb8"
    return content == template or sha256(content).hexdigest() == older_guide


def setup_maintenance(harness, source, *, online=False):
    """Install project-owned maintenance files and migrate known legacy links."""
    root = harness.source_directory(source)
    if harness.root.is_relative_to(root):
        raise ProjectError("The project directory cannot contain the central working area")
    current_mode = project_maintenance_mode(root)
    bindings = harness.bindings()
    project_id = next((name for name, value in bindings.items()
                       if harness.bound_path(value).resolve() == root), None)
    new_registration = online and project_id is None and current_mode is not False
    if new_registration:
        project_id = identity(re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-"))
        if project_id in bindings:
            raise ProjectError(
                f"Project name {project_id!r} is already registered at a different path. "
                "Register this checkout with a distinct name, then run setup-maintenance --online."
            )
    state = state_path(harness, project_id) if project_id else None
    installed = json.loads(state.read_text(encoding="utf-8")) if state and state.exists() else {}
    selected = current_mode
    if selected is None:
        selected = online or bool(project_id and installed.get("settings", {}).get("skills"))
    if online and not selected:
        raise ProjectError("The item has been explicitly selected for offline; change directly when switch is granted .researchharness/mode.toml")

    bundle = Path(__file__).with_name("standalone")
    directory = root / ".researchharness"
    agent = root / "AGENTS.md"
    ignore = root / ".gitignore"
    files = ("maintain.py", "offline/check.py", "offline/operations.md")
    for path in (directory / "offline", directory / "online", agent, ignore,
                 *(directory / name for name in files)):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ProjectError(f"Project maintenance documents must be in the project and use a normal file or directory:{path}")

    text = agent.read_text(encoding="utf-8") if agent.exists() else ""
    if START in text or END in text:
        text = agent_text(text, "")
    if text.count(MODE_START) != text.count(MODE_END) or text.count(MODE_START) > 1:
        raise ProjectError("AGENTS.md Maintenance mode paragraph tag incomplete")
    section = (bundle / "agents.md").read_text(encoding="utf-8").rstrip()
    block = f"{MODE_START}\n{section}\n{MODE_END}"
    if MODE_START in text:
        before, rest = text.split(MODE_START, 1)
        _, after = rest.split(MODE_END, 1)
        text = before + block + after
    else:
        separator = "\n\n" if text.strip() else ""
        text = f"{text.rstrip()}{separator}{block}\n"
    text = with_search_guidance(text)

    created = {}
    preserved = []
    for name in files:
        path = directory / name
        if path.exists():
            if not path.is_file():
                raise ProjectError(f"Maintenance of entrance requires normal files:{path}")
            # Upgrade copies of previous bundled files while preserving project edits.
            bundled_digests = {
                "maintain.py": {
                    "a8b2e1c7dd3d636bad4c4434a82a6863e0d002ff4f3ba9ff8d4a430a580086ce",
                    "35765f8ea768e47d73ef78b15a53725026851d05c30bd736f084cd26d51d690c",
                    "24ce82adfa5db609700b9180f235359cef1af76c9d99db6a7763011536da2907",
                    "d6f9e100bdeb2306484befe1c60769a54a3353d21b77729138c2092ef0b17a72",
                    "56497b92162da21ff1d985eb104bfa42a48e52e7863c7773b123df0dbbee726c",
                },
                "offline/check.py": {
                    "368ddb3cd5ddd6c80ee3cf523227f3f7c06f6cc486f7cf4d97bd7c516cade9b3",
                },
            }
            if sha256(path.read_bytes()).hexdigest() not in bundled_digests.get(name, ()):
                preserved.append(name)
                continue
        created[path] = (bundle / name).read_bytes()
    ignore_text = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    comment = "# EverResearch stores machine-specific connection records here."
    if ONLINE_IGNORE not in ignore_text.splitlines():
        separator = "\n\n" if ignore_text.strip() else ""
        updated_ignore = ignore_text.rstrip() + f"{separator}{comment}\n{ONLINE_IGNORE}\n"
    else:
        updated_ignore = ignore_text
    backup = None
    legacy_plan = None
    if current_mode is None:
        legacy_plan = legacy_skill_changes(harness, root, installed)
        paths = {*created, *legacy_plan[0], agent, ignore, directory / "mode.toml"}
        if selected and project_id:
            paths.add(directory / "online/connection.json")
        backup = save_initial_backup(root, paths)
        for rule in (BACKUP_IGNORE, BACKUP_LOCK_IGNORE):
            if rule not in updated_ignore.splitlines():
                updated_ignore = updated_ignore.rstrip() + f"\n{rule}\n"
    if new_registration:
        harness.register(project_id, str(root), replace=False)
    remove_legacy_backup_lock(root)
    if updated_ignore != ignore_text:
        save_bytes(ignore, updated_ignore.encode(), source=__file__)
    for path, content in created.items():
        save_bytes(path, content, source=__file__)
    if not agent.exists() or text != agent.read_text(encoding="utf-8"):
        save_bytes(agent, text.encode(), source=__file__)
    if current_mode is None:
        save_bytes(directory / "mode.toml",
                   ("# Purpose and main function: Selection of the source of the project maintenance rules.\n"
                    "# Scope: The project launcher and EverResearch read this setting to select online or offline maintenance.\n"
                    f"enabled = {str(selected).lower()}\n").encode(), source=__file__)
    attached = False
    if selected and project_id:
        apply(harness, project_id)
        attached = True
    else:
        remove_legacy_skill_files(harness, root, installed, plan=legacy_plan)
    return {"project": str(root), "mode": "online" if selected else "offline",
            "attached": attached, "preserved": preserved, "backup": str(backup) if backup else None}


def status(harness, project_id):
    _, root, value = settings(harness, project_id)
    project_mode = project_maintenance_mode(root)
    if project_mode is not None:
        value["skills"] = project_mode
    expected = catalogue(harness) if value["skills"] else {}
    state = state_path(harness, project_id)
    applied = json.loads(state.read_text(encoding="utf-8")) if state.exists() else None
    guide = online_guide(harness, project_id) if project_mode else root / "AGENTS.md"
    return {
        "project_id": project_id,
        "path": str(root),
        "settings": value,
        "skills": {name: True for name in expected},
        "shared_skill_directory": str(harness.root / ".agents/skills") if value["skills"] else None,
        "skill_entry": ("central-guide" if project_mode else "AGENTS.md") if value["skills"] else None,
        "maintenance_guide": str(guide) if value["skills"] and guide.is_file() else None,
        "resources": resources.read(harness, project_id),
        "last_applied_settings": (
            {"lightweight_checks": False, **applied["settings"]} if applied else None
        ),
    }


def status_by_path(source, harness_root=None):
    """Report maintenance readiness without writing to or running code from the project."""
    root = Path(source).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ProjectError(f"Expected a project directory: {root}")

    report = {"path": str(root), "state": "unmanaged", "mode": None, "guide": None}
    directory = root / ".researchharness"
    try:
        mode = project_maintenance_mode(root)
        if mode is False:
            report["mode"] = "offline"
            require_file(directory / "maintain.py")
            require_file(directory / "offline/check.py")
            guide = require_file(directory / "offline/operations.md")
        elif mode is True:
            report["mode"] = "online"
            require_file(directory / "maintain.py")
            connection = json.loads(require_file(directory / "online/connection.json").read_text(
                encoding="utf-8"
            ))
            central = (root / connection["root"]).resolve(strict=True)
            if connection.get("installed") is True:
                harness = HarnessContext(installed_resources(), central)
            else:
                require_file(central / "src/harness/cli.py")
                require_file(central / "src/harness/projects/operations.md")
                harness = load_harness(central)
            guide = check_online_guide(root, status(harness, connection["project_id"]), central)
        else:
            agents = root / "AGENTS.md"
            text = agents.read_text(encoding="utf-8") if agents.is_file() and not agents.is_symlink() else ""
            if (directory / "mode.json").is_file():
                raise ProjectError(
                    "The old .researchharness/mode.json does not select a current mode. "
                    "Choose a mode and run rh projects setup-maintenance <project-path> "
                    "(add --online for online maintenance)."
                )
            if MODE_START in text or MODE_END in text or (directory / "maintain.py").exists():
                raise ProjectError(
                    ".researchharness/mode.toml is missing. Choose a mode and run "
                    "rh projects setup-maintenance <project-path> (add --online for online maintenance)."
                )
            if START not in text and END not in text:
                return report
            if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
                raise ProjectError("The EverResearch section in AGENTS.md is incomplete.")
            report["mode"] = "legacy"
            harness = load_harness(harness_root)
            project_id = next((name for name, path in harness.bindings().items()
                               if harness.bound_path(path).resolve() == root), None)
            if project_id is None:
                raise ProjectError("The project uses an older EverResearch setup without a matching local registration.")
            binding = status(harness, project_id)
            if not binding["settings"]["skills"]:
                return {**report, "reason": "Shared skills are disabled for this project."}
            if not binding["skills"] or not binding["maintenance_guide"]:
                raise ProjectError("The registered EverResearch skills or project guide are unavailable.")
            guide = agents
    except (OSError, ValueError, KeyError, TypeError, AttributeError, yaml.YAMLError) as error:
        return {**report, "state": "unavailable", "reason": str(error)}
    return {**report, "state": "managed", "guide": str(guide)}


def apply(harness, project_id, changes=None):
    with update_lock(state_path(harness, identity(project_id))):
        return apply_skills(harness, project_id, changes)


def apply_skills(harness, project_id, changes):
    path, root, original = settings(harness, project_id)
    project_mode = project_maintenance_mode(root)
    if project_mode is not None and changes and "skills" in changes:
        raise ProjectError("This item is by: .researchharness/mode.toml controls;rechanging the contents of enabled Value")
    if project_mode is False:
        raise ProjectError("Project maintenance switch is closed; please use the offline entry on the project belt")
    value = {**original, **(changes or {})}
    if project_mode is True:
        value["skills"] = True
    state = state_path(harness, project_id)
    installed = json.loads(state.read_text(encoding="utf-8")) if state.exists() else {}
    desired = catalogue(harness) if value["skills"] else {}
    root_agent = root / "AGENTS.md"
    if root_agent.is_symlink():
        raise ProjectError(f"Access requires normal files of the project itself:{root_agent}")
    root_text = root_agent.read_text(encoding="utf-8") if root_agent.exists() else ""
    guide = root_agent
    connection = None
    if project_mode:
        if ".researchharness/mode.toml" not in root_text:
            raise ProjectError("Item AGENTS.md You have to explain first. .researchharness/mode.toml The two entrances.")
        guide = online_guide(harness, project_id)
        connection = root / ".researchharness/online/connection.json"
        if connection.is_symlink() or connection.parent.is_symlink():
            raise ProjectError(f"Online connection records must be located within the project:{connection}")

    original_guide = root_text if guide == root_agent else ""
    updated_guide = agent_text(original_guide, guidance(harness, project_id, value, desired, guide))
    if guide == root_agent:
        updated_agent = updated_guide
    elif START in root_text or END in root_text:
        updated_agent = agent_text(root_text, "")
    else:
        updated_agent = root_text
    updated_agent = with_search_guidance(updated_agent)
    settings_text = updated_settings(path, project_id, changes) if changes else None
    remove_legacy_skill_files(harness, root, installed)
    if guide != root_agent:
        save_bytes(guide, updated_guide.encode(), source=__file__)
    if updated_agent != root_text:
        save_bytes(root_agent, updated_agent.encode(), source=__file__)
    if connection is not None:
        runtime = {"python": sys.executable}
        if harness.state is not None:
            runtime = {"installed": True}
            plugin_cli = os.environ.get("RH_PLUGIN_CLI")
            if plugin_cli:
                runtime["plugin_cli"] = plugin_cli
            else:
                cli = Path(sys.executable).with_name("rh.exe" if os.name == "nt" else "rh")
                if cli.is_file():
                    runtime["cli"] = str(cli)
                elif on_path := shutil.which("rh"):
                    runtime["cli"] = on_path
        save(connection, {
            "purpose": "Central working area for online maintenance of positioning projects.",
            "scope": "Only for project maintenance switches to read on.",
            "root": str(relative_or_absolute(harness.state_root, root)),
            **runtime,
            "project_id": project_id,
        }, source=__file__)
    if settings_text is not None:
        save_bytes(path, settings_text.encode(), source=__file__)
    save(
        state,
        {
            "purpose": "Record applied project maintenance settings.",
            "scope": "For Project Access Query and Mode Migration.",
            "settings": value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        source=__file__,
    )
    return status(harness, project_id)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness-root")
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("status", "apply", "set", "register", "resources", "bind", "install", "run"):
        command = commands.add_parser(action)
        if action == "run":
            command.add_argument("--env", action="append", default=[], metavar="NAME=VALUE")
        command.add_argument("project")
        if action == "set":
            command.add_argument("--skills", choices=["on", "off"], required=True)
        elif action == "apply":
            command.add_argument(
                "--lightweight-checks", choices=["on", "off"],
                help="Save permissions for this modified light-validation machine and omit the original settings",
            )
        elif action == "register":
            command.add_argument("--path", required=True)
        elif action == "bind":
            command.add_argument("--data", action="append", default=[])
            command.add_argument("--remove-data", action="append", default=[])
            interpreter = command.add_mutually_exclusive_group()
            interpreter.add_argument("--python")
            interpreter.add_argument("--clear-python", action="store_true")
        elif action == "install":
            command.add_argument("--requirements", required=True, metavar="FILE")
            command.add_argument("--preserve-package", action="append", default=[], metavar="NAME")
        elif action == "run":
            command.add_argument("arguments", nargs=argparse.REMAINDER)
    commands.add_parser("list")
    setup_parser = commands.add_parser("setup-maintenance", help="Maintenance portals to be used independently for project delivery")
    setup_parser.add_argument("path")
    setup_parser.add_argument("--online", action="store_true", help="Register and enable online maintenance for this checkout")
    maintenance_check = commands.add_parser("maintenance", help="Increased acceptance and inspection items and updated central maintenance index")
    maintenance_check.add_argument("path")
    maintenance_check.add_argument("--fresh", action="store_true", help="Recheck all structural conditions")
    maintenance_check.add_argument("--limit", type=int, default=20, help="Maximum number of bars per group in summary")
    maintenance_check.add_argument("--record", metavar="JSON", help="Maintenance of access, problems and validation records")
    project_check = commands.add_parser("project", help="Inspect or check a research project")
    project_commands = project_check.add_subparsers(dest="project_operation", required=True)
    project_status = project_commands.add_parser(
        "status", help="Report maintenance readiness by path without running project code",
    )
    project_status.add_argument("path")
    project_checker = project_commands.add_parser("check", help="Preview onboarding or check project structure")
    project_checker.add_argument("path")
    mode = project_checker.add_mutually_exclusive_group()
    mode.add_argument("--onboarding", action="store_true", help="Show a read-only onboarding plan")
    mode.add_argument("--strict", action="store_true", help="Check the project's required structure")
    project_checker.add_argument("--json", action="store_true",
                                 help="Return the strict JSON report, or an onboarding report with --onboarding")
    layout = commands.add_parser("layout", help="Examination of the layout of scientific projects")
    layout_commands = layout.add_subparsers(dest="layout_operation", required=True)
    layout_commands.add_parser("check", help="Run a read-only tree-based check by project path").add_argument("path")
    experiment = commands.add_parser("experiment", help="Check the lab execution records and the official product.")
    experiment.add_subparsers(dest="experiment_operation", required=True).add_parser(
        "check", help="Check the identity, effective configuration, file name and complete path for each execution",
    ).add_argument("path")
    precheck = commands.add_parser("precheck", help="Check the evidence for automatic precheck at the public entry point.")
    precheck_check = precheck.add_subparsers(dest="precheck_operation", required=True).add_parser(
        "check", help="Read a record of successful and failed precheck",
    )
    precheck_check.add_argument("path")
    precheck_check.add_argument("succeeded")
    precheck_check.add_argument("rejected")
    precheck_check.add_argument("--max-seconds", required=True, type=float)
    precheck_check.add_argument("--max-samples", required=True, type=int)
    reviews = commands.add_parser("structure").add_subparsers(dest="operation", required=True)
    for operation in ("add", "list", "show", "review"):
        command = reviews.add_parser(operation)
        command.add_argument("project")
        if operation == "add":
            command.add_argument("html")
            command.add_argument("--revision", required=True)
            command.add_argument("--scope", required=True)
        if operation in {"show", "review"}:
            command.add_argument("artifact")
        if operation == "review":
            command.add_argument("--decision", choices=["approved", "changes-requested"], required=True)
            command.add_argument("--note", default="")
    args = parser.parse_args(argv)
    try:
        if args.action == "project":
            if args.project_operation == "status":
                print(json.dumps(status_by_path(args.path, args.harness_root), ensure_ascii=False, indent=2))
                return 0
            root = Path(args.path).resolve(strict=True)
            configured = (root / ".researchharness/mode.toml").is_file()
            if args.onboarding or not (configured or args.strict or args.json):
                result = onboarding.preview(root)
                print(json.dumps(result, ensure_ascii=False, indent=2) if args.json
                      else onboarding.format_preview(result))
                return 0
            result = check_project(root)
            if configured and not (args.strict or args.json or result["passed"]):
                report = onboarding.preview(root, remaining_fixes=len(result["violations"]))
                print(onboarding.format_preview(report))
                return 0
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.json
                  else onboarding.format_check(result))
            return 0 if result["passed"] else 1
        checks = {"layout": check_layout, "experiment": check_experiment}
        if args.action in checks:
            result = checks[args.action](args.path)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["passed"] else 1
        if args.action == "precheck":
            result = check_precheck(
                args.path, args.succeeded, args.rejected,
                max_seconds=args.max_seconds, max_samples=args.max_samples,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["passed"] else 1
        harness = load_harness(args.harness_root)
        if args.action == "setup-maintenance":
            result = setup_maintenance(harness, args.path, online=args.online)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.action == "maintenance":
            result = maintenance.check(
                harness, args.path, fresh=args.fresh, limit=args.limit, record=args.record,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["project_check"]["passed"] else 1
        project = getattr(args, "project", None)
        if args.action == "list":
            result = [
                {"project": name, "path": str(harness.bound_path(path)), **resources.read(harness, name)}
                for name, path in sorted(harness.bindings().items())
            ]
        elif args.action == "register":
            result = {"project": project, "path": str(harness.register(project, args.path))}
        elif args.action == "status":
            result = status(harness, project)
        elif args.action == "apply":
            changes = (
                {"lightweight_checks": args.lightweight_checks == "on"}
                if args.lightweight_checks is not None else None
            )
            result = apply(harness, project, changes)
        elif args.action == "set":
            result = apply(harness, project, {"skills": args.skills == "on"})
        elif args.action == "resources":
            harness.project_root(project)
            result = resources.read(harness, project)
        elif args.action == "bind":
            result = resources.update(harness, project, data=args.data, remove_data=args.remove_data,
                                      python=args.python, clear_python=args.clear_python)
        elif args.action == "install":
            return resources.install(harness, project, args.requirements,
                                     preserve_packages=args.preserve_package)
        elif args.action == "run":
            arguments = args.arguments
            if arguments[:1] == ["--"]:
                arguments = arguments[1:]
            return resources.run(harness, project, arguments, environment=args.env)
        elif args.operation == "add":
            result = structure.register(harness, project, args.html, args.revision, args.scope)
        elif args.operation == "list":
            result = structure.list_reviews(harness, project)
        elif args.operation == "show":
            result = structure.show(harness, project, args.artifact)
        else:
            result = structure.review(harness, project, args.artifact, args.decision, args.note)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
