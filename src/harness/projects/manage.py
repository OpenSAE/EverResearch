"""同步共享技能并分发本机项目资源与结构成果操作。

用于已明确选择工作区和项目的 rh projects 命令。
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

from harness.central import ProjectError, find_harness, identity, load_harness
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
        raise ProjectError("项目共享设置的 skills 使用 true/false")
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
        raise ProjectError(f"共享技能目录需要位于项目工作区内：{directory}")
    return directory


def guidance(harness, project_id, value, directory, desired):
    root = harness.root
    project_root = directory.parent.parent
    workspace = harness.workspace
    if workspace is not None and project_root.is_relative_to(workspace):
        root = Path(os.path.relpath(root, project_root))
    skills = "已开启" if value["skills"] else "已关闭"
    skill_path = directory.relative_to(project_root)
    skill_entry = f"项目接入说明位于 `{skill_path}/researchharness/SKILL.md`。"
    if directory.name == "researchharness-skills" and desired:
        skill_entry += "\n按当前任务读取以下共享技能的 `SKILL.md`：\n\n"
        skill_entry += "\n".join(f"- `{skill_path / name / 'SKILL.md'}`" for name in desired)
    return f"""{START}
## ResearchHarness 共同维护

本项目标识为 `{project_id}`。从项目根目录访问中央入口 `{root}`，共享技能{skills}。
工程维护沿本项目的实际入口和调用关系。若中央有 `src/project/{project_id}/README.md`，可查阅项目经验和工程入口。
项目代码审阅、计划和授权沿用本项目的 GitHub 流程与当前会话授权。
人类提供研究目的、体验反馈与投入偏好，助手承担授权内的工程判断和持续处理。
值得长期保存的人类思想按 HumanInterface 整理，展示完整草稿并取得认可后保存。
项目接入由 `rh projects status {project_id}` 查询，用户开关指令由 `rh projects set` 应用。
本机数据与 Python 选择通过 `rh projects resources {project_id}` 查询。

{skill_entry}
{END}"""


def agent_text(text, block):
    """Update only the owned section, preserving the project's other instructions."""
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ProjectError("AGENTS.md 中的项目接入段落标记不完整")
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
        "client_reload": "新会话读取接入技能与权限；已有会话按客户端实际加载状态重新加载。",
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
        raise ProjectError("现有共享技能位置已变化，请核对上次应用记录和项目技能目录")
    desired = known if value["skills"] else {}
    for name, target in targets.items():
        if name not in desired and name not in previous:
            continue
        link = directory / name
        if link.exists() or link.is_symlink():
            if not link.is_symlink() or link.resolve() not in {target, previous.get(name)}:
                raise ProjectError(f"保留项目自有技能 {link}；请明确同名技能的接入方式")
    agent = root / "AGENTS.md"
    entry = directory / "researchharness/SKILL.md"
    for file in (agent, entry):
        if file.is_symlink() or not file.resolve().is_relative_to(root):
            raise ProjectError(f"接入说明需要项目自身的普通文件：{file}")
    updated_agent = agent_text(
        agent.read_text() if agent.exists() else "",
        guidance(harness, project_id, value, directory, desired),
    )
    directory.mkdir(parents=True, exist_ok=True)
    for name in targets:
        link = directory / name
        if name not in desired and link.is_symlink() and link.resolve() in {targets[name], previous.get(name)}:
            link.unlink()
    workspace = harness.workspace
    for name, target in desired.items():
        link = directory / name
        destination = target
        if workspace is not None and root.is_relative_to(workspace):
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
            text = ("# 项目共享技能开关，供 rh projects 读取。\n"
                    f"project_id: {project_id}\nskills: {str(value['skills']).lower()}\n")
        save_bytes(path, text.encode(), source=__file__)
    save(
        state,
        {
            "purpose": "记录已应用的项目技能、权限选择和接入文件。",
            "scope": "本项目的共享技能链接、协作说明与开发模式。",
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
    for action in ("status", "apply", "set", "register", "resources", "bind", "run"):
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
        elif action == "run":
            command.add_argument("arguments", nargs=argparse.REMAINDER)
    commands.add_parser("init-workspace", help="在 ResearchHarness 的上一级初始化工作区和 data/")
    commands.add_parser("list")
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
        harness = load_harness(args.harness_root or find_harness())
        project = getattr(args, "project", None)
        if args.action == "init-workspace":
            workspace = harness.init_workspace()
            result = {"workspace": str(workspace), "harness": str(harness.root),
                      "data": str(workspace / "data")}
        elif args.action == "list":
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
