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
import sys
import tomllib

import yaml

from harness.central import ProjectError, identity, load_harness
from harness.core.experiment import check_experiment
from harness.core.layout import check_layout
from harness.core.check import check_precheck
from harness.core.project import check_project
from harness.core.workspace import save, save_bytes, update_lock
from . import maintenance, resources, structure

START = "<!-- researchharness:projects -->"
END = "<!-- /researchharness:projects -->"
MODE_START = "<!-- researchharness:mode -->"
MODE_END = "<!-- /researchharness:mode -->"
SEARCH_START = "<!-- researchharness:search -->"
SEARCH_END = "<!-- /researchharness:search -->"
SEARCH_GUIDANCE = '## Locate projects and files\n\nStart with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.'
ONLINE_IGNORE = "/.researchharness/online/"
MAINTENANCE_SKILLS = {
    "maintain-project": "Project-wide access, inspection or cross-component maintenance",
    "maintain-base": "Access, configuration synthesis, distribution of components or common operation",
    "maintain-dataset": "Dataset, sample reading, labeling, sorting or cache",
    "maintain-model": "Model, variant, construction or weight load",
    "maintain-task": "Task calculation, pre-check, indicator or outcome interface",
    "maintain-conf": "Open Parameters, Defaults, Configure Presets or Overwrite Orders",
    "maintain-experiment": "Configure, run, restore or read the results of a single experiment",
    "maintain-optional": "Independent script, test, document or external file",
    "maintain-code": "Code review, duplicate realization or functional gap",
    "maintain-tmp": "One-time clean-up and temporary engineering work",
    "maintain-skill": "Assessment and maintenance skills per se",
    "maintain-knowledge": "Collating and preserving research knowledge and thinking",
}

PROJECT_ACTIONS = (
    ("Reading, research, planning", "read", "Existing access, configuration and records"),
    ("Maintenance of public access and operation", "base", "`base/` and existing root entrances"),
    ("Modify datasets achieved", "datasets", "`datasets/`"),
    ("Modified model realization", "models", "`models/`"),
    ("Modify Task or Precheck", "tasks", "`tasks/`"),
    ("Modify Open Configuration", "conf", "`conf/`"),
    ("Run experiments or read back results", "experiment", "public entry point and `experiment/`"),
    ("Prepare test or assistive scripts", "tests-scripts", "`tests/`,`scripts/` or responsible for its realization"),
    ("Create a one-time file or code", "tmp", "`tmp/<Purpose>/`"),
    ("Update the operating environment", "environment", "already bound environment and `doc/environment/`"),
    ("Download and prepare data", "data", "Workspace `data/<Data Set>/<Version>/`"),
    ("Retention of reusable resources", "assets", "`assets/<Type>/<Resources>/` Or the original cache root"),
    ("Maintenance of third-party source code", "third-party", "`third_party/<Upstream>/`"),
    ("Update Document", "doc", "`doc/` and current navigation"),
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
        raise ProjectError(".researchharness/mode.toml Need to be specified enabled = true or false")
    return data["enabled"]


def online_guide(harness, project_id):
    return harness.resolve(f".workspace/harness/projects/manage/guide_{identity(project_id)}.md")


def maintenance_guidance(skill_path, operations_path, desired, lightweight_checks):
    if not desired:
        return ""
    lines = [
        "### Daily maintenance and lightweight checks",
        "",
        "**Choose the operation before making changes.** Before editing, moving files, installing, downloading, or running a command, "
        "Puts the action under one of the functions in the following table, opens the corresponding guidance and implements the section ’ s judgement, implementation and end steps."
        "Cross-component requests multiple actions and separate categories. Each class reads the corresponding guidelines and applies prior to the first operation. `SKILL.md`."
        "The path in the guidance is broken down by the root of the item, and the parent area resources are based on the actual position attached.",
        "",
        "**When asked to implement a feature, follow these steps.**",
        "",
        "1. Write out which entry the user will provide, what results to see, and select a small sample to complete the judgement."
        "Along README Nearest current command, trace to configuration, responsible for realization and result reading position.",
        "2. Identify the kind of change. If an existing parameter supports the request, use the current recipe or command-line option. "
        "Change in existing components when it is achieved; when independent input, behaviour or selection,"
        "Adds a named component to the corresponding existing level I directory..",
        "3. Change responsibility to achieve first, then connect to registration, configuration, distribution and readback that requires change. Sync defaults and documents when new public options are available;"
        "Use the existing results to write to the entry when changing the task output, register the product and keep the old field in use."
        "The code that needs to be checked first, put in the existing one. `tmp/<Purpose>/`,Relocation after completion by return, tool or official function.",
        "4. Validate target behaviour with a minimum input from the same entry, check the actual generation path and read back."
        "Perform approved structural checks when the path changes and update user-accessible notes.",
        "",
        "For example, to add per-class accuracy to an existing classification task, start with its evaluation and report. "
        "Calculate indicators in the final mission assessment and maintain them through an existing experimental recorder; check the indicators with a fixed sample and read them back through the normal entrance."
        "Increase configuration only if the user needs an independent switch.",
        "",
        "| Operational guidance | Main position |",
        "| --- | --- |",
        *(f"| [{action}](<{operations_path.as_posix()}#{section}>) | {destination} |"
          for action, section, destination in PROJECT_ACTIONS),
        "",
        "**Use the established layout.** For daily tasks, keep the existing top-level directories and use their designated paths. "
        "Keep intermediate output out of the project root. Before running a command, confirm its working directory, output paths, and cache location. "
        "Read only the survey when the classification is not clear, and write when applicable duties and compliance points are identified."
        "A clear project access or restructuring authorization is required for the first time when a standard catalogue or a restructuring of the overall structure is required.",
        "",
        "**Review the paths after each batch.** Inspect new, moved, and generated files, and correct any misplaced output before continuing. "
        "The change was found to result in the non-adoption of the structure, which was repaired and delivered.",
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
        lines.extend(("", "| Maintain content | First-reading skills |", "| --- | --- |", *rows))
    if lightweight_checks:
        lines.extend((
            "",
            "**Lightweight follow-up checks are enabled.** After the change, run the smallest relevant check through the normal entry point. "
            "Use when adding, deleting, moving, changing name or changing output path `rh projects layout check`."
            "For the whole project `rh projects project check`,Available when central index is approved for writing `rh projects maintenance` Reuse Structure Results."
            "Run one structure check for each state of the project tree. "
            "Experimental records and precheck evidence as required `rh projects experiment check` and `rh projects precheck check`."
            "Prioritize existing light testing, configuration preview or pre-check for behavioural change, using available resources and peer input."
            "Downloads, installations, official scientific operations and large-scale calculations carried out on a mission basis.",
            "",
            "When delivered, describe the entry point, the behaviour covered and the results.,"
            "Complete the check that can be done and indicate which part of the behavior is still lacking operational evidence..",
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
## ResearchHarness Optional access

The project itself. README Provides installation, configuration and running access..
Our own resources are available. `rh projects resources {project_id}` Question.
{END}"""
    operations_path = relative_or_absolute(harness.root / "src/harness/projects/operations.md", guide.parent)
    skill_path = relative_or_absolute(harness.root / ".agents/skills", guide.parent)
    notes = harness.project_record(project_id) / "README.md"
    notes_path = relative_or_absolute(notes, guide.parent)
    workflow = maintenance_guidance(skill_path, operations_path, desired, value["lightweight_checks"])
    return f"""{START}
## ResearchHarness Online maintenance

### Purpose

Provision of projects `{project_id}` Central Operations Guidance, Original Skills Entry and Light Validation Options.

### Scope

For this item to select an online maintenance item. README Provide independent means of installation, configuration and operation.
Project maintenance follows the physical access and call relationships of the project. GitHub Process & Current Session Authorization.
Central engineering experience records, if maintained `{notes_path}` View. This machine data is linked to Python Select with `rh projects resources {project_id}` Query. Skills links point directly at ResearchHarness Original in warehouse.{workflow}
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


def remove_legacy_skill_files(harness, root, installed):
    """Remove central-generated aliases and guides, preserving project-owned content."""
    known = catalogue(harness)
    previous = {name: harness.root / target for name, target in installed.get("links", {}).items()}
    for relative in (".agents/skills", ".agents/researchharness-skills",
                     ".researchharness/online/skills"):
        directory = root / relative
        if (directory.is_symlink() or not directory.resolve().is_relative_to(root)
                or not directory.is_dir()):
            continue
        removed = False
        for name in known.keys() | previous.keys():
            link = directory / name
            if link.is_symlink() and link.resolve() in {known.get(name), previous.get(name)}:
                link.unlink()
                removed = True
        entry = directory / "researchharness/SKILL.md"
        if remove_legacy_skill_guide(root, entry):
            removed = True
            if not any(entry.parent.iterdir()):
                entry.parent.rmdir()
        if removed and not any(directory.iterdir()):
            directory.rmdir()

    remove_legacy_skill_guide(root, root / ".researchharness/legacy/connection_guide.md")
    guide = root / ".researchharness/online/README.md"
    if (guide.is_file() and not guide.is_symlink() and not guide.parent.is_symlink()
            and guide.resolve().is_relative_to(root)):
        original = guide.read_text(encoding="utf-8")
        if START in original:
            remaining = agent_text(original, "")
            if remaining.strip():
                save_bytes(guide, remaining.encode(), source=__file__)
            else:
                guide.unlink()


def remove_legacy_skill_guide(root, path):
    if (path.is_symlink() or path.parent.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(root)):
        return False
    content = path.read_bytes()
    template = Path(__file__).with_name("researchharness.skill.md.in").read_bytes()
    # Recognize the previous distributed guide as well as the last template.
    older_guide = "e0adfe5c565832c410fc914bd4518d8878c594b82810f598d2a67751d57cdcb8"
    if content == template or sha256(content).hexdigest() == older_guide:
        path.unlink()
        return True
    return False


def setup_maintenance(harness, source, *, online=False):
    """Install project-owned maintenance files and migrate known legacy links."""
    root = harness.source_directory(source)
    if harness.root.is_relative_to(root):
        raise ProjectError("The project directory cannot contain the central working area")
    current_mode = project_maintenance_mode(root)
    project_id = next((name for name, value in harness.bindings().items()
                       if harness.bound_path(value).resolve() == root), None)
    if online and project_id is None:
        raise ProjectError("Online access requires the registration of projects before running. setup-maintenance --online")
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
            # Upgrade only the released launcher that still expects project-local skills.
            old_launchers = {
                "a8b2e1c7dd3d636bad4c4434a82a6863e0d002ff4f3ba9ff8d4a430a580086ce",
                "35765f8ea768e47d73ef78b15a53725026851d05c30bd736f084cd26d51d690c",
            }
            if name != "maintain.py" or sha256(path.read_bytes()).hexdigest() not in old_launchers:
                preserved.append(name)
                continue
        created[path] = (bundle / name).read_bytes()
    for path, content in created.items():
        save_bytes(path, content, source=__file__)
    ignore_text = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    if ONLINE_IGNORE not in ignore_text.splitlines():
        comment = "# Connection records maintained online on-line."
        separator = "\n\n" if ignore_text.strip() else ""
        save_bytes(ignore, (ignore_text.rstrip() + f"{separator}{comment}\n{ONLINE_IGNORE}\n").encode(),
                   source=__file__)
    if not agent.exists() or text != agent.read_text(encoding="utf-8"):
        save_bytes(agent, text.encode(), source=__file__)
    if current_mode is None:
        save_bytes(directory / "mode.toml",
                   ("# Purpose and main function: Selection of the source of the project maintenance rules.\n"
                    "# Scope of application: AGENTS.md,Project maintenance entrance and central mounted reading.\n"
                    f"enabled = {str(selected).lower()}\n").encode(), source=__file__)
    attached = False
    if selected and project_id:
        apply(harness, project_id)
        attached = True
    else:
        remove_legacy_skill_files(harness, root, installed)
    return {"project": str(root), "mode": "online" if selected else "offline",
            "attached": attached, "preserved": preserved}


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
        save(connection, {
            "purpose": "Central working area for online maintenance of positioning projects.",
            "scope": "Only for project maintenance switches to read on.",
            "root": str(relative_or_absolute(harness.state_root, root)),
            **({"installed": True} if harness.state is not None else {}),
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
    setup_parser.add_argument("--online", action="store_true", help="Enable online access to registered items when first configured")
    maintenance_check = commands.add_parser("maintenance", help="Increased acceptance and inspection items and updated central maintenance index")
    maintenance_check.add_argument("path")
    maintenance_check.add_argument("--fresh", action="store_true", help="Recheck all structural conditions")
    maintenance_check.add_argument("--limit", type=int, default=20, help="Maximum number of bars per group in summary")
    maintenance_check.add_argument("--record", metavar="JSON", help="Maintenance of access, problems and validation records")
    project_check = commands.add_parser("project", help="Check project responsibilities and document structure")
    project_check.add_subparsers(dest="project_operation", required=True).add_parser(
        "check", help="Check five essential catalogues, real components, component position, number of files and tree-wide path",
    ).add_argument("path")
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
        checks = {"project": check_project, "layout": check_layout, "experiment": check_experiment}
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
