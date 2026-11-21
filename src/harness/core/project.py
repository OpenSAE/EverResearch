"""Number of level I duties, component locations, direct documents and subdirectories checked for scientific projects.

Read-only central entrance for project maintenance. Repeat the fine layout rules and report from disk
The use of the components and the original behaviour are further demonstrated by the public entry point of the project..
"""

import ast
import json
import re
from pathlib import Path

import yaml

from .experiment import read_record
from .layout import CODE, COMPONENTS, CONFIG, NAME, check_layout


REQUIRED = ("base", *COMPONENTS.values(), "conf")
FILE_LIMIT = 15
DIRECTORY_REVIEW_THRESHOLD = 15
COMPONENT_NAMES = {*COMPONENTS, *COMPONENTS.values()}


def visible(directory):
    return sorted(
        entry for entry in directory.iterdir()
        if not entry.name.startswith(".") and entry.name != "__pycache__"
    )


def directories(root):
    yield root
    for entry in visible(root):
        if entry.is_dir() and not entry.is_symlink():
            yield from directories(entry)


def has_source(path):
    if path.is_symlink() or not path.is_file() or not re.fullmatch(CODE, path.name):
        return False
    if path.suffix in {".pyi", ".h", ".hpp", ".cuh"}:
        return False
    if path.suffix == ".py":
        try:
            syntax = ast.parse(path.read_bytes(), filename=str(path))
        except (SyntaxError, ValueError, UnicodeError):
            return False
        for node in ast.walk(syntax):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(
                    not isinstance(statement, (ast.Pass, ast.Raise))
                    and not (
                        isinstance(statement, ast.Expr)
                        and isinstance(statement.value, ast.Constant)
                    )
                    and not (
                        isinstance(statement, ast.Return)
                        and (statement.value is None or isinstance(statement.value, ast.Constant)
                             or (isinstance(statement.value, ast.Name)
                                 and statement.value.id == "NotImplemented"))
                    )
                    for statement in node.body
                ):
                    return True
        return False
    source = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".ipynb":
        try:
            return any(
                cell.get("cell_type") == "code" and any(str(line).strip() for line in cell.get("source", ()))
                for cell in json.loads(source)["cells"]
            )
        except (ValueError, KeyError, TypeError, AttributeError):
            return False
    return any(line.strip() and not line.lstrip().startswith(("#", "//", "--", "%"))
               for line in source.splitlines())


def implementations(directory):
    return any(has_source(path) for subdir in directories(directory) for path in visible(subdir))


def has_configuration(directory):
    for path in visible(directory):
        if (path.is_symlink() or not path.is_file() or path.stem != "config"
                or not re.fullmatch(CONFIG, path.name)):
            continue
        try:
            if read_record(path):
                return True
        except (ValueError, yaml.YAMLError):
            continue
    return False


def markdown_text(path):
    if not path.is_file() or path.is_symlink():
        return ""
    return re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)


def check_project(root):
    """Return the detailed layout report plus mandatory project-wide constraints."""
    result = check_layout(root)
    root = Path(result["project"])
    violations = result["violations"]
    components = {}
    directory_reviews = []

    def fail(path, rule, expected):
        violations.append({"path": path, "rule": rule, "expected": expected})

    def real_directory(path):
        return path.is_dir() and not path.is_symlink()

    for name in REQUIRED:
        if not real_directory(root / name):
            fail(name, "required_directory", f"The project must have an entity at its root {name}/ Contents")

    base = root / "base"
    if real_directory(base):
        if not implementations(base):
            fail("base", "base_implementation", "Includes official access, distribution or shared operations")
        for directory in directories(base):
            for path in visible(directory):
                if path.is_dir() and path.name in COMPONENT_NAMES:
                    relative = path.relative_to(root).as_posix()
                    fail(relative, "nested_component", "Component achieved at the end of the project datasets/,models/ or tasks/,Original import preserves through package map")

    for role, name in COMPONENTS.items():
        directory = root / name
        if not real_directory(directory):
            components[role] = []
            continue
        members = [
            entry.name for entry in visible(directory)
            if real_directory(entry) and re.fullmatch(NAME, entry.name)
            and (role != "task" or entry.name != "precheck") and implementations(entry)
        ]
        components[role] = members
        if not members:
            expected = "At least one named component catalogue containing the actual implementable component source code"
            if role == "task":
                expected += ";precheck It’s a precheck, and the official research mission is carried out on its own."
            fail(name, "component_implementation", expected)
        if role == "task":
            precheck = directory / "precheck"
            if not real_directory(precheck) or not implementations(precheck):
                fail("tasks/precheck", "precheck_implementation", "Provision of actual formal precheck")

    conf = root / "conf"
    if real_directory(conf) and not has_configuration(conf):
        fail("conf", "configuration_entry", "Provides a list of names and profiles conf/config.<format> Unified Configuration Entry")

    environment = root / "doc/environment"
    environment_readme = environment / "README.md"
    if (not real_directory(root / "doc") or not real_directory(environment)
            or not any(line.strip() and not line.lstrip().startswith("#")
                       for line in markdown_text(environment_readme).splitlines())):
        fail("doc/environment/README.md", "environment_documentation",
             "Provision of readable environmental statements, recording of installation, operational readiness, validation orders and physical environmental sources")
    index = root / "doc/README.md"
    if not re.search(
        r"\]\(\s*<?(?:\./)?environment/README\.md(?:#[^\s)>]*)?>?(?:\s+[^)]*)?\)",
        markdown_text(index),
    ):
        fail("doc/README.md", "environment_navigation", "Presented to environment/README.md Local Markdown Link")

    code_roots = [root / name for name in ("base", "tasks", "scripts", "tests")]
    for violation in violations:
        if violation["rule"] == "root_directory":
            candidate = root / violation["path"]
            if candidate.name == "src" or (candidate / "__init__.py").is_file():
                code_roots.append(candidate)

    for start in code_roots:
        if real_directory(start):
            for directory in directories(start):
                entries = visible(directory)
                subdirs = sum(real_directory(entry) for entry in entries)
                files = len(entries) - subdirs
                relative = directory.relative_to(root).as_posix()
                if files > FILE_LIMIT:
                    fail(relative, "directory_file_count",
                         f"Up to direct files {FILE_LIMIT} - Yeah, actually. {files} individual;grouping by function and checking for duplicates")
                if subdirs > DIRECTORY_REVIEW_THRESHOLD:
                    directory_reviews.append({
                        "path": relative,
                        "rule": "directory_child_count",
                        "files": files,
                        "directories": subdirs,
                        "expected": "Reconcile the duties and calls of the direct subdirectories, merge and duplicate and group them according to actual commonality",
                    })

    violations.sort(key=lambda item: (item["path"], item["rule"]))
    directory_reviews.sort(key=lambda item: item["path"])
    return {**result, "passed": not violations, "components": components,
            "directory_reviews": directory_reviews}
