"""Synchronize the sharing of skills and the distribution of project resources and structural results.

For defined selection of workspaces and projects rh projects Command.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

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
MAINTENANCE_SKILLS = {
    "maintain-project": "Onboarding and project-wide maintenance",
    "maintain-base": "Entry points, configuration, dispatch, and runtime",
    "maintain-dataset": "Datasets, sample loading, labels, splits, and caches",
    "maintain-model": "Model variants, construction, and checkpoint loading",
    "maintain-task": "Task computation, prechecks, metrics, and results",
    "maintain-conf": "Public settings, defaults, presets, and overrides",
    "maintain-experiment": "Configure, run, resume, or inspect an experiment",
    "maintain-optional": "Standalone scripts, tests, docs, and external files",
    "maintain-code": "Code review, duplication, and missing behavior",
    "maintain-tmp": "Temporary engineering work and investigation",
    "maintain-skill": "Evaluate and maintain skills",
    "maintain-knowledge": "Maintain research notes",
}

PROJECT_ACTIONS = (
    ("Read, investigate, or plan", "read", "Existing entry points, settings, and records"),
    ("Maintain shared entry points", "base", "`base/` and existing root entry points"),
    ("Change a dataset implementation", "datasets", "`datasets/`"),
    ("Change a model", "models", "`models/`"),
    ("Change a task or precheck", "tasks", "`tasks/`"),
    ("Change public configuration", "conf", "`conf/`"),
    ("Run or inspect an experiment", "experiment", "Public entry point and `experiment/`"),
    ("Write a test or script", "tests-scripts", "`tests/`, `scripts/`, or the owning component"),
    ("Create temporary files or code", "tmp", "`tmp/<purpose>/`"),
    ("Update the runtime environment", "environment", "Bound environment and `doc/environment/`"),
    ("Download and prepare data", "data", "`data/<dataset>/<version>/` or the bound data root"),
    ("Keep reusable assets", "assets", "`assets/<type>/<resource>/` or the configured cache"),
    ("Maintain third-party code", "third-party", "`third_party/<upstream>/`"),
    ("Update documentation", "doc", "`doc/` and existing navigation"),
)


def settings(harness, project_id):
    """Read the explicit user choice and check its existing project binding."""
    project_id = identity(project_id)
    path = harness.project_record(project_id, "project.yaml")
    root = harness.project_root(project_id)
    value = yaml.safe_load(path.read_text()) if path.exists() else {"skills": True}
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
    original = path.read_text()
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


def skill_directory(root):
    """Keep a project's repository-wide skill alias dedicated to its original target."""
    default = root / ".agents/skills"
    directory = root / ".agents/researchharness-skills" if default.is_symlink() else default
    if directory.is_symlink() or not directory.resolve().is_relative_to(root):
        raise ProjectError(f"Shared skills directories need to be located in the project area:{directory}")
    return directory


def maintenance_guidance(skill_path, operations_path, desired, lightweight_checks):
    if not desired:
        return ""
    lines = [
        "### Daily maintenance and lightweight checks",
        "",
        "**Classify each operation before acting.** Before an edit, move, install, download, "
        "or command, choose a row below and follow its procedure. Split cross-component "
        "requests into separate operations. Before the first action of each kind, read its guide "
        "and the applicable `SKILL.md`. Resolve project paths from the project root and "
        "shared resources from their actual bindings.",
        "",
        "**When asked to implement a feature:**",
        "",
        "1. Define the user-facing entry point, input, expected result, and a small acceptance case. "
        "Trace the closest documented command to its configuration, implementation, and reader.",
        "2. If an existing setting meets the request, use it. Extend the current component when it "
        "owns the behavior. Add a named component under its existing top-level directory when it "
        "has an independent input, behavior, or selection.",
        "3. Change the owning implementation, then connect any needed registry entries, settings, "
        "dispatch, and result readers. Keep supported output fields and reuse the existing recorder. "
        "Put one-time probes under the existing `tmp/<purpose>/` and decide what to retain afterward.",
        "4. Verify with a small input through the same entry point. Check the actual "
        "output path and readback. Run authorized structure checks when paths change and update docs.",
        "",
        "For example, add per-class accuracy to the existing classification task by extending its "
        "final evaluation and using its current report writer. Check fixed labels and predictions, "
        "then read the report back through the normal interface. Add a setting only if users need "
        "to choose whether to include the metric.",
        "",
        "| Operation guide | Destination |",
        "| --- | --- |",
        *(f"| [{action}](<{operations_path.as_posix()}#{section}>) | {destination} |"
          for action, section, destination in PROJECT_ACTIONS),
        "",
        "**Use the existing top-level directories.** Daily tasks stay within existing compliant "
        "locations. Keep top-level directory names and avoid temporary output at the root. "
        "Confirm the command's working directory, output, and cache locations before running it. "
        "Use read-only investigation until an unclear write has a defined category and destination. "
        "Creating a standard top-level directory or restructuring requires explicit authorization.",
        "",
        "**Check paths after each batch.** Compare new, moved, and generated paths with the intended "
        "destinations. Correct layout violations introduced by this work before continuing.",
    ]
    rows = [
        f"| {purpose} | [`{name}`]({(skill_path / name / 'SKILL.md').as_posix()}) |"
        for name, purpose in MAINTENANCE_SKILLS.items()
        if name in desired
    ]
    if rows:
        lines.extend(("", "| Maintenance area | Skill to read |", "| --- | --- |", *rows))
    if lightweight_checks:
        lines.extend((
            "",
            "**Lightweight follow-up checks are enabled.** Use the smallest applicable check through "
            "the normal entry point. Use `rh projects layout check` when paths or output locations "
            "change. For a project-wide check, use `rh projects project check` or the authorized "
            "`rh projects maintenance` index. Use one structure check per tree state. "
            "Use experiment or precheck evidence commands only when relevant. Reuse focused tests, "
            "configuration previews, or prechecks with existing local resources and bounded inputs. "
            "Downloads, installs, and full research runs follow the task's authorization.",
            "",
            "Report the actual entry point, coverage, results, and any behavior that still needs evidence.",
        ))
    else:
        lines.extend(("", "**Lightweight follow-up checks require task authorization.** "
                      "When authorized, reuse central checks and the project's existing checks."))
    return "\n\n" + "\n".join(lines)


def guidance(harness, project_id, value, directory, desired):
    root = harness.root
    project_root = directory.parent.parent
    if project_root.is_relative_to(harness.workspace):
        root = Path(os.path.relpath(root, project_root))
    skills = "enabled" if value["skills"] else "disabled"
    project_notes = harness.project_record(project_id).relative_to(harness.root) / "README.md"
    skill_path = directory.relative_to(project_root)
    skill_entry = f"See `{skill_path}/researchharness/SKILL.md` for the connection guide."
    if directory.name == "researchharness-skills" and desired:
        other_skills = sorted(desired.keys() - MAINTENANCE_SKILLS.keys())
        if other_skills:
            skill_entry += "\n\n Other available shared skills\n\n"
            skill_entry += "\n".join(f"- `{skill_path / name / 'SKILL.md'}`" for name in other_skills)
    operations_path = root / "src/harness/projects/operations.md"
    workflow = maintenance_guidance(skill_path, operations_path, desired, value["lightweight_checks"])
    return f"""{START}
## ResearchHarness connection

Use the project's README, dependency declarations, and normal entry points to install, configure, and run it.
The registered project ID is `{project_id}`. The ResearchHarness root is `{root}` and shared skills are {skills.lower()}.
Resolve relative paths from the project root. Project notes, when available, are at `{project_notes}` under the ResearchHarness root.

Follow project review and authorization rules and the current request.
Use `rh projects status {project_id}` to inspect the connection, `rh projects set` to change shared skill settings, and `rh projects resources {project_id}` to see local data and Python bindings.

{skill_entry}{workflow}
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


def status(harness, project_id):
    _, root, value = settings(harness, project_id)
    expected = catalogue(harness)
    links = skill_directory(root)
    actual = {
        name: (links / name).is_symlink() and (links / name).resolve() == target
        for name, target in expected.items()
    }
    state = state_path(harness, project_id)
    applied = json.loads(state.read_text()) if state.exists() else None
    return {
        "project_id": project_id,
        "path": str(root),
        "settings": value,
        "skills": actual,
        "shared_skill_directory": str(links),
        "skill_entry": "project-skill-directory" if links.name == "skills" else "AGENTS.md",
        "resources": resources.read(harness, project_id),
        "last_applied_settings": (
            {"lightweight_checks": False, **applied["settings"]} if applied else None
        ),
        "client_reload": "New session to read shared skills; already existing session reloads by actual loading status of client.",
    }


def apply(harness, project_id, changes=None):
    with update_lock(state_path(harness, identity(project_id))):
        return apply_skills(harness, project_id, changes)


def apply_skills(harness, project_id, changes):
    path, root, original = settings(harness, project_id)
    value = {**original, **(changes or {})}
    known = catalogue(harness)
    state = state_path(harness, project_id)
    old = json.loads(state.read_text()) if state.exists() else {}
    installed = old.get("links", {})
    previous = {name: harness.root / target for name, target in installed.items()}
    # Adopt earlier hand-installed central links, so the off switch also removes them.
    targets = {**previous, **known}
    directory = skill_directory(root)
    if installed and root / old.get("directory", ".agents/skills") != directory:
        raise ProjectError("Existing shared skills positions have changed, and please check last application log and project skills directory")
    desired = known if value["skills"] else {}
    for name, target in targets.items():
        if name not in desired and name not in previous:
            continue
        link = directory / name
        if link.exists() or link.is_symlink():
            if not link.is_symlink() or link.resolve() not in {target, previous.get(name)}:
                raise ProjectError(f"Retention of project-owned skills {link};Please specify how the same-named skill is accessed.")
    agent = root / "AGENTS.md"
    entry = directory / "researchharness/SKILL.md"
    for file in (agent, entry):
        if file.is_symlink() or not file.resolve().is_relative_to(root):
            raise ProjectError(f"Access requires normal files of the project itself:{file}")
    updated_agent = agent_text(
        agent.read_text() if agent.exists() else "",
        guidance(harness, project_id, value, directory, desired),
    )
    settings_text = updated_settings(path, project_id, changes) if changes else None
    directory.mkdir(parents=True, exist_ok=True)
    for name in targets:
        link = directory / name
        if name not in desired and link.is_symlink() and link.resolve() in {targets[name], previous.get(name)}:
            link.unlink()
    for name, target in desired.items():
        link = directory / name
        destination = target
        if root.is_relative_to(harness.workspace):
            destination = Path(os.path.relpath(target, directory))
        if not link.is_symlink():
            link.symlink_to(destination, target_is_directory=True)
        elif link.readlink() != destination:
            link.unlink()
            link.symlink_to(destination, target_is_directory=True)
    save_bytes(agent, updated_agent.encode(), source=__file__)
    save_bytes(entry, Path(__file__).with_name("researchharness.skill.md.in").read_bytes(), source=__file__)
    if settings_text is not None:
        save_bytes(path, settings_text.encode(), source=__file__)
    save(
        state,
        {
            "purpose": "Record applied project skills and access documents.",
            "scope": "Project shared skills links and collaboration notes.",
            "settings": value,
            "directory": directory.relative_to(root).as_posix(),
            "links": {name: target.relative_to(harness.root).as_posix() for name, target in desired.items()},
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
