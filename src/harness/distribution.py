"""Find release resources, diagnose an installation, and manage project skill copies.

Used by rh guide, rh doctor, and rh skills in source and installed environments.
"""

import argparse
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import platform
import shutil
import tempfile

from .central import ProjectError, identity, load_harness
from .core.workspace import update_lock

AGENTS = {
    "claude-code": ".claude/skills",
    "codex": ".agents/skills",
    "cursor": ".agents/skills",
    "deepseek-harness": ".dsh/skills",
    "gemini-cli": ".gemini/skills",
    "github-copilot": ".github/skills",
    "opencode": ".agents/skills",
    "openclaw": ".agents/skills",
    "qwen-code": ".qwen/skills",
    "generic": ".agents/skills",
}
GUIDES = {
    "project-agreement": "src/harness/projects/README.md",
    "operations": "src/harness/projects/operations.md",
    "example": "src/harness/projects/templates/cub",
}
RECEIPT = ".researchharness-install.json"
PREVIOUS = ".researchharness-previous-"


def release_version():
    try:
        return version("researchharness")
    except PackageNotFoundError:
        return "source"


def skill_location(context, name):
    return context.resolve(f".agents/skills/{identity(name)}/SKILL.md", exists=True)


def skill_state(context, name):
    source = skill_location(context, name).parent
    if context.state is None:
        return source
    return context.resolve(f".workspace/skills/{name}")


def doctor(context, project):
    detected = {
        name: bool(shutil.which(command))
        for name, command in {
            "claude-code": "claude", "codex": "codex", "cursor": "cursor-agent",
            "deepseek-harness": "dsh", "gemini-cli": "gemini", "github-copilot": "copilot",
            "opencode": "opencode", "openclaw": "openclaw", "qwen-code": "qwen",
        }.items()
    }
    resource_names = (".agents/skills/maintain-project/SKILL.md", *GUIDES.values())
    return {
        "version": release_version(), "system": platform.system(),
        "python": platform.python_version(), "mode": "installed" if context.state else "source",
        "resources": {name: context.resolve(name).exists() for name in resource_names},
        "state_directory": str(context.state_root), "data_directory": str(context.data_root),
        "project": str(project) if project else None,
        "commands_detected": detected,
    }


def checksums(directory):
    records = {}
    for member in sorted(directory.rglob("*")):
        if member.is_symlink():
            raise ProjectError(f"Symlink found in skill: {member}")
        if member.is_file() and member.name != RECEIPT:
            records[member.relative_to(directory).as_posix()] = sha256(member.read_bytes()).hexdigest()
    return records


def owned(target, name=None):
    receipt = target / RECEIPT
    if target.is_symlink() or receipt.is_symlink() or not receipt.is_file():
        raise ProjectError(f"Skill has no ResearchHarness installation receipt: {target}")
    record = json.loads(receipt.read_text(encoding="utf-8"))
    if (record.get("owner") != "researchharness" or record.get("skill") != (name or target.name)
            or record.get("files") != checksums(target)):
        raise ProjectError(f"Installed skill has local changes: {target}")
    return record


def install_skills(context, project, agents, *, operation, dry_run):
    sources = context.resolve(".agents/skills", exists=True)
    if operation == "install" and context.state is None:
        raise ProjectError("Install the release wheel before distributing project skills")
    directories = sorted({(project / AGENTS[agent]) for agent in agents})
    for directory in directories:
        if not directory.resolve().is_relative_to(project):
            raise ProjectError(f"Skill directory escapes the selected project: {directory}")
    results = []
    if not dry_run and operation == "install":
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    for directory in directories:
        if dry_run:
            results.extend(change_skills(sources, directory, operation, dry_run=True))
        else:
            with update_lock(directory.parent / (directory.name + ".researchharness")):
                results.extend(change_skills(sources, directory, operation, dry_run=False))
    return results


def change_skills(sources, directory, operation, *, dry_run):
    backups = {}
    if directory.is_dir():
        for backup in directory.glob(f"{PREVIOUS}*"):
            name = identity(backup.name.removeprefix(PREVIOUS))
            owned(backup, name=name)
            target = directory / name
            if target.exists() or target.is_symlink():
                owned(target)
                if not dry_run:
                    shutil.rmtree(backup)
            elif dry_run:
                backups[name] = backup
            else:
                backup.replace(target)
    if operation == "install":
        names = sorted(item.name for item in sources.iterdir() if (item / "SKILL.md").is_file())
    elif directory.is_dir():
        names = sorted(set(backups) | {
            item.name for item in directory.iterdir()
            if not item.name.startswith(".") and (item / RECEIPT).exists()
        })
    else:
        names = []
    records = []
    for name in names:
        target = directory / name
        existing = backups.get(name, target)
        previous = owned(existing, name=name) if existing.exists() or existing.is_symlink() else None
        source = sources / name
        desired = ({"owner": "researchharness", "skill": name, "version": release_version(),
                    "files": checksums(source)} if operation == "install" else None)
        action = ("unchanged" if desired == previous else operation)
        records.append((source, target, desired, action))
    if not dry_run:
        for source, target, desired, action in records:
            if action == "unchanged":
                continue
            with tempfile.TemporaryDirectory(prefix=".researchharness-", dir=directory) as scratch:
                staged = Path(scratch) / "skill"
                previous = directory / f"{PREVIOUS}{target.name}"
                if desired:
                    shutil.copytree(source, staged)
                    (staged / RECEIPT).write_text(json.dumps(desired, indent=2), encoding="utf-8")
                if target.exists():
                    target.replace(previous)
                try:
                    if desired:
                        staged.replace(target)
                except OSError:
                    if previous.exists():
                        previous.replace(target)
                    raise
                if previous.exists():
                    shutil.rmtree(previous)
    return [{"action": action, "path": str(target)} for _, target, _, action in records]


def main(command, argv):
    parser = argparse.ArgumentParser(prog=f"rh {command}")
    parser.add_argument("--harness-root", type=Path)
    if command == "guide":
        parser.add_argument("kind", choices=[*GUIDES, "skill", "skill-state"])
        parser.add_argument("name", nargs="?")
    elif command == "doctor":
        parser.add_argument("--project", type=Path)
        parser.add_argument("--json", action="store_true")
    else:
        parser.add_argument("operation", choices=["install", "uninstall"])
        parser.add_argument("--project", type=Path, required=True)
        parser.add_argument("--agent", choices=AGENTS, action="append")
        parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        context = load_harness(args.harness_root)
        if command == "guide":
            if args.kind in {"skill", "skill-state"}:
                if args.name is None:
                    parser.error(f"{args.kind} requires a skill name")
                result = (skill_location(context, args.name) if args.kind == "skill"
                          else skill_state(context, args.name))
            else:
                if args.name is not None:
                    parser.error(f"{args.kind} takes no skill name")
                result = context.resolve(GUIDES[args.kind], exists=True)
            print(result)
        elif command == "doctor":
            project = context.source_directory(args.project) if args.project else None
            report = doctor(context, project)
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print(f"ResearchHarness {report['version']} ({report['mode']}) on {report['system']}")
                print(f"State: {report['state_directory']}")
                for name, available in report["resources"].items():
                    print(f"{'ok' if available else 'missing'}  {name}")
            return 0 if all(report["resources"].values()) else 1
        else:
            project = context.source_directory(args.project)
            report = install_skills(context, project, args.agent or ["generic"],
                                    operation=args.operation, dry_run=args.dry_run)
            print(json.dumps(report, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")
    return 0
