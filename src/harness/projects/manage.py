"""Synchronize shared skills and manage local project resources and structure maps.

Implements the rh projects commands for a selected workspace and project.
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
from harness.core.precheck import check_precheck
from harness.core.project import check_project
from harness.core.workspace import save, save_bytes, update_lock
from . import resources, structure

START = "<!-- researchharness:projects -->"
END = "<!-- /researchharness:projects -->"


def settings(harness, project_id):
    """Read the explicit user choice and check its existing project binding."""
    project_id = identity(project_id)
    path = harness.resolve(f"src/project/{project_id}/project.yaml")
    root = harness.project_root(project_id)
    value = yaml.safe_load(path.read_text()) if path.exists() else {"skills": True}
    if (
        not isinstance(value, dict)
        or value.get("project_id", project_id) != project_id
        or type(value.get("skills")) is not bool
    ):
        raise ProjectError("Project Sharing Settings skills use true/false")
    return path, root, {"skills": value["skills"]}


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


def guidance(harness, project_id, value, directory, desired):
    root = harness.root
    project_root = directory.parent.parent
    if project_root.is_relative_to(harness.workspace):
        root = Path(os.path.relpath(root, project_root))
    skills = "enabled" if value["skills"] else "disabled"
    skill_path = directory.relative_to(project_root)
    skill_entry = f"See `{skill_path}/researchharness/SKILL.md` for project setup."
    if directory.name == "researchharness-skills" and desired:
        skill_entry += "\n Read the shared skill that matches the current task:\n\n"
        skill_entry += "\n".join(f"- `{skill_path / name / 'SKILL.md'}`" for name in desired)
    return f"""{START}
## ResearchHarness workspace integration

This project's README, requirements, and public commands describe how to install, configure, and run it independently.
This workspace registers the project as `{project_id}` and uses ResearchHarness at `{root}`, with shared skills {skills}. Resolve relative paths from the project root. The central checkout may provide project notes in `src/project/{project_id}/README.md`.
Follow the project's actual entry points and callers when maintaining it.
Follow the project's GitHub workflow and the current authorization for code reviews and plans.
Researchers set goals and give feedback. Assistants make engineering decisions within the authorized scope.
Use `maintain-knowledge` to preserve research notes when the skill is available.
View the connection with `rh projects status {project_id}`. Change shared skill settings with `rh projects set`.
View data and Python bindings with `rh projects resources {project_id}`.

{skill_entry}
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
        "last_applied_settings": {"skills": applied["settings"]["skills"]} if applied else None,
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
    save_bytes(entry, (Path(__file__).parent / "researchharness.skill.md").read_bytes(), source=__file__)
    if changes:
        if path.exists():
            text = re.sub(r"^skills:.*$", f"skills: {str(value['skills']).lower()}",
                          path.read_text(), flags=re.MULTILINE)
        else:
            text = ("# Project shared skills switches for rh projects Read.\n"
                    f"project_id: {project_id}\nskills: {str(value['skills']).lower()}\n")
        save_bytes(path, text.encode(), source=__file__)
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
    project_check = commands.add_parser("project", help="Check project responsibilities and document structure")
    project_check.add_subparsers(dest="project_operation", required=True).add_parser(
        "check", help="Check required directories, component source, per-directory file counts, and paths",
    ).add_argument("path")
    layout = commands.add_parser("layout", help="Check project naming and layout")
    layout_commands = layout.add_subparsers(dest="layout_operation", required=True)
    layout_commands.add_parser("check", help="Run a read-only tree-based check by project path").add_argument("path")
    experiment = commands.add_parser("experiment", help="Check experiment records and declared outputs")
    experiment.add_subparsers(dest="experiment_operation", required=True).add_parser(
        "check", help="Check the identity, effective configuration, file name and complete path for each execution",
    ).add_argument("path")
    precheck = commands.add_parser("precheck", help="Check evidence that the public entry point ran precheck")
    precheck_check = precheck.add_subparsers(dest="precheck_operation", required=True).add_parser(
        "check", help="Check a successful run and one blocked by precheck",
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
            result = apply(harness, project)
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
