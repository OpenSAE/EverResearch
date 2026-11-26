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
from .layout import CODE, COMPONENTS, CONFIG, NAME, check_layout, project_paths


REQUIRED = ("base", *COMPONENTS.values(), "conf")
FILE_LIMIT = 15
DIRECTORY_REVIEW_THRESHOLD = 15
COMPONENT_NAMES = {*COMPONENTS, *COMPONENTS.values()}


def visible(directory, paths):
    return sorted(
        entry for entry in directory.iterdir()
        if (paths is None or entry in paths) and not entry.name.startswith(".") and entry.name != "__pycache__"
    )


def directories(root, paths):
    yield root
    for entry in visible(root, paths):
        if entry.is_dir() and not entry.is_symlink():
            yield from directories(entry, paths)


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


def implementations(directory, remember, paths):
    return any(remember(path, has_source) for subdir in directories(directory, paths)
               for path in visible(subdir, paths))


def populated_configuration(path):
    try:
        return bool(read_record(path))
    except (ValueError, yaml.YAMLError):
        return False


def has_configuration(directory, remember, paths):
    for path in visible(directory, paths):
        if (path.is_symlink() or not path.is_file() or path.stem != "config"
                or not re.fullmatch(CONFIG, path.name)):
            continue
        if remember(path, populated_configuration):
            return True
    return False


def markdown_text(path):
    if not path.is_file() or path.is_symlink():
        return ""
    return re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)


def environment_documented(path):
    return any(line.strip() and not line.lstrip().startswith("#")
               for line in markdown_text(path).splitlines())


def environment_linked(path):
    return bool(re.search(
        r"\]\(\s*<?(?:\./)?environment/README\.md(?:#[^\s)>]*)?>?(?:\s+[^)]*)?\)",
        markdown_text(path),
    ))


def check_project(root, *, remember=None):
    """Return the detailed layout report plus mandatory project-wide constraints."""
    root = Path(root).resolve(strict=True)
    paths = project_paths(root)
    result = check_layout(root, remember=remember, paths=paths)
    if remember is None:
        def remember(path, inspect):
            return inspect(path)
    root = Path(result["project"])
    violations = result["violations"]
    components = {}
    directory_reviews = []

    def fail(path, rule, expected):
        violations.append({"path": path, "rule": rule, "expected": expected})

    def real_directory(path):
        return (paths is None or path in paths) and path.is_dir() and not path.is_symlink()

    for name in REQUIRED:
        directory = root / name
        if not real_directory(directory):
            message = (f"Expected a real directory at the project root: {name}/"
                       if directory.exists() or directory.is_symlink()
                       else f"Missing required directory: {name}/")
            fail(name, "required_directory", message)

    base = root / "base"
    if real_directory(base):
        if not implementations(base, remember, paths):
            fail("base", "base_implementation", "Add a working entry point, dispatcher, or shared implementation under base/.")
        for directory in directories(base, paths):
            for path in visible(directory, paths):
                if path.is_dir() and path.name in COMPONENT_NAMES:
                    relative = path.relative_to(root).as_posix()
                    fail(relative, "nested_component", "Move the component to datasets/, models/, or tasks/ and preserve public imports through the package mapping.")

    for role, name in COMPONENTS.items():
        directory = root / name
        if not real_directory(directory):
            components[role] = []
            continue
        members = [
            entry.name for entry in visible(directory, paths)
            if real_directory(entry) and re.fullmatch(NAME, entry.name)
            and (role != "task" or entry.name != "precheck") and implementations(entry, remember, paths)
        ]
        components[role] = members
        if not members:
            expected = "Add at least one named component directory with a working implementation."
            if role == "task":
                expected += " The project needs a scientific task in addition to tasks/precheck/."
            fail(name, "component_implementation", expected)
        if role == "task":
            precheck = directory / "precheck"
            if not real_directory(precheck) or not implementations(precheck, remember, paths):
                fail("tasks/precheck", "precheck_implementation", "Add a working precheck under tasks/precheck/.")

    conf = root / "conf"
    if real_directory(conf) and not has_configuration(conf, remember, paths):
        fail("conf", "configuration_entry", "Add a nonempty main configuration file at conf/config.<format>.")

    environment = root / "doc/environment"
    environment_readme = environment / "README.md"
    if (not real_directory(root / "doc") or not real_directory(environment)
            or (paths is not None and environment_readme not in paths)
            or not remember(environment_readme, environment_documented)):
        fail("doc/environment/README.md", "environment_documentation",
             "Document dependencies, setup, resources, and verification commands in doc/environment/README.md.")
    index = root / "doc/README.md"
    if (paths is not None and index not in paths) or not remember(index, environment_linked):
        fail("doc/README.md", "environment_navigation", "Add a relative Markdown link to environment/README.md in doc/README.md.")

    code_roots = [root / name for name in ("base", "tasks", "scripts", "tests")]
    for violation in violations:
        if violation["rule"] == "root_directory":
            candidate = root / violation["path"]
            if candidate.name == "src" or (candidate / "__init__.py").is_file():
                code_roots.append(candidate)

    for start in code_roots:
        if real_directory(start):
            for directory in directories(start, paths):
                entries = visible(directory, paths)
                subdirs = sum(real_directory(entry) for entry in entries)
                files = len(entries) - subdirs
                relative = directory.relative_to(root).as_posix()
                if files > FILE_LIMIT:
                    fail(relative, "directory_file_count",
                         f"This directory has {files} files. The limit is {FILE_LIMIT}. Group related files and check for duplicates.")
                if subdirs > DIRECTORY_REVIEW_THRESHOLD:
                    directory_reviews.append({
                        "path": relative,
                        "rule": "directory_child_count",
                        "files": files,
                        "directories": subdirs,
                        "expected": "Review how the subdirectories are used and group related ones by purpose.",
                    })

    violations.sort(key=lambda item: (item["path"], item["rule"]))
    directory_reviews.sort(key=lambda item: item["path"])
    return {**result, "passed": not violations, "components": components,
            "directory_reviews": directory_reviews}
