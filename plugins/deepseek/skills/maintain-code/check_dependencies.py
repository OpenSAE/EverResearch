"""Check the core component’s dependent boundary and experiment Code Files in.

For maintain-code Read-only scanned target items. Output contains source files, line numbers and dependencies;
Dynamic calculations of paths and operating configurations continue to be checked by skill processes.
"""

import argparse
import ast
from collections import deque
from functools import cache
from importlib.util import resolve_name
import os
from pathlib import Path
import shlex
import sys
import tomllib


CORE = {"base", "models", "tasks", "datasets"}
CODE_SUFFIXES = {
    ".bash", ".c", ".cc", ".class", ".clj", ".cpp", ".cs", ".cu", ".cuh", ".cxx",
    ".dll", ".dylib", ".exe", ".fish", ".go", ".h", ".hpp", ".ipynb", ".java",
    ".jl", ".js", ".jsx", ".kt", ".lua", ".m", ".mjs", ".php", ".pl", ".ps1",
    ".py", ".pyc", ".pyi", ".pyo", ".r", ".rb", ".rs", ".s", ".sbatch", ".scala",
    ".sh", ".so", ".sql", ".swift", ".ts", ".tsx", ".wasm", ".zsh",
}
CODE_NAMES = {"CMakeLists.txt", "Dockerfile", "GNUmakefile", "Makefile", "makefile"}
IMPORT_CALLS = {"__import__", "importlib.import_module"}
LOAD_CALLS = {"importlib.util.spec_from_file_location", "runpy.run_path"}
READ_CALLS = {
    "joblib.load", "numpy.load", "numpy.loadtxt", "pandas.read_csv", "pandas.read_json",
    "pandas.read_parquet", "PIL.Image.open", "torch.load", "os.listdir", "os.scandir",
}
COMMAND_CALLS = {
    "os.system", "subprocess.Popen", "subprocess.call", "subprocess.check_call",
    "subprocess.check_output", "subprocess.run",
}
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def module_paths(root, mappings, module, *, include_parents=True):
    """Resolve local imports and their package initializers in dotted-name order."""
    if not module:
        return
    parts = module.split(".")
    depths = range(1, len(parts) + 1) if include_parents else (len(parts),)
    for depth in depths:
        name = ".".join(parts[:depth])
        for prefix, directory in mappings:
            if prefix and name != prefix and not name.startswith(prefix + "."):
                continue
            suffix = name[len(prefix):].lstrip(".")
            location = directory.joinpath(*suffix.split(".")) if suffix else directory
            choices = (location / "__init__.py", location.with_suffix(".py")) if suffix else (
                location / "__init__.py",
            )
            for candidate in choices:
                if candidate.is_file() and candidate.is_relative_to(root):
                    yield candidate
                    break
            else:
                if depth == len(parts) and location.is_dir() and location.is_relative_to(root):
                    relative = location.relative_to(root)
                    if relative.parts and relative.parts[0] not in CORE:
                        yield location
                continue
            break


def module_package(source, mappings):
    for prefix, directory in mappings:
        if source.is_relative_to(directory):
            package = ".".join(source.parent.relative_to(directory).parts)
            return ".".join(part for part in (prefix, package) if part)
    return ""


def import_base(node, package):
    parts = package.split(".") if package else []
    if node.level > len(parts):
        return None
    parent = parts[:len(parts) - node.level + 1] if node.level else []
    return ".".join(parent + ([node.module] if node.module else []))


def imports(node, package):
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    base = import_base(node, package)
    if base is None:
        return []
    return [base, *[".".join(filter(None, (base, alias.name))) for alias in node.names]]


def qualified_name(node, aliases):
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        return qualified_name(node.value, aliases) + "." + node.attr
    return ""


def local_paths(root, value):
    if isinstance(value, (str, Path)) and value:
        path = Path(value)
        yield root / path


def path_value(node, source, root, values, aliases):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return values.get(node.id)
    if isinstance(node, ast.Attribute):
        name = qualified_name(node, {})
        if name in values:
            return values[name]
    if isinstance(node, ast.Attribute) and node.attr == "parent":
        value = path_value(node.value, source, root, values, aliases)
        if isinstance(value, Path):
            return value.parent
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
        if node.value.attr == "parents" and isinstance(node.slice, ast.Constant):
            value = path_value(node.value.value, source, root, values, aliases)
            index = node.slice.value
            if isinstance(value, Path) and type(index) is int and 0 <= index < len(value.parents):
                return value.parents[index]
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)):
        left = path_value(node.left, source, root, values, aliases)
        right = path_value(node.right, source, root, values, aliases)
        if isinstance(node.op, ast.Div) and isinstance(left, Path) and isinstance(right, (str, Path)):
            return left / right
        if isinstance(node.op, ast.Add) and isinstance(left, str) and isinstance(right, str):
            return left + right
    if isinstance(node, ast.Call):
        return path_call_value(node, source, root, values, aliases)
    return None


def path_call_value(node, source, root, values, aliases):
    name = qualified_name(node.func, aliases)
    arguments = [path_value(arg, source, root, values, aliases) for arg in node.args]
    if name in {"pathlib.Path.cwd", "Path.cwd", "os.getcwd"}:
        return root
    if name in {"pathlib.Path", "Path", "os.path.join"} and all(
        isinstance(arg, (str, Path)) for arg in arguments
    ):
        return Path(*arguments)
    if isinstance(node.func, ast.Attribute):
        receiver = path_value(node.func.value, source, root, values, aliases)
        if isinstance(receiver, Path):
            if node.func.attr in {"resolve", "absolute"}:
                return (root / receiver).resolve()
            if node.func.attr == "joinpath" and all(isinstance(arg, (str, Path)) for arg in arguments):
                return receiver.joinpath(*arguments)
    return None


def argument(call, index, *names):
    if len(call.args) > index:
        return call.args[index]
    return next((item.value for item in call.keywords if item.arg in names), None)


def read_mode(mode):
    return mode is None or (
        isinstance(mode, ast.Constant) and isinstance(mode.value, str)
        and ("r" in mode.value or "+" in mode.value)
    )


def command_target(arguments):
    if not arguments or not isinstance(arguments[0], (str, Path)):
        return None
    executable = Path(arguments[0])
    if executable.name.startswith("python") or executable.name in {"sh", "bash", "zsh"}:
        for index, item in enumerate(arguments[1:], start=1):
            if not isinstance(item, (str, Path)):
                return None
            if item == "-c":
                return None
            if item == "-m":
                module = arguments[index + 1] if index + 1 < len(arguments) else None
                return ("import", module) if isinstance(module, str) else None
            if not str(item).startswith("-"):
                return "command", item
    elif "/" in str(arguments[0]) or executable.suffix in {".py", ".sh"}:
        return "command", arguments[0]
    return None


def call_targets(call, source, root, values, aliases):
    name = qualified_name(call.func, aliases)

    def value(node):
        return path_value(node, source, root, values, aliases)

    first = argument(call, 0, "name")
    if name in IMPORT_CALLS or name == "runpy.run_module":
        target = value(first)
        if isinstance(target, str) and target:
            package = value(argument(call, 1, "package"))
            if not target.startswith("."):
                yield "import", target
            elif isinstance(package, str) and package:
                try:
                    yield "import", resolve_name(target, package)
                except ImportError:
                    pass
    if name in LOAD_CALLS:
        index = int(name == "importlib.util.spec_from_file_location")
        yield "read", value(argument(call, index, "location", "path_name"))
    if name in {"open", "io.open", "builtins.open"} and read_mode(argument(call, 1, "mode")):
        yield "read", value(argument(call, 0, "file"))
    if name in READ_CALLS:
        yield "read", value(argument(call, 0, "f", "file", "fname", "filepath_or_buffer", "fp", "path"))
    if isinstance(call.func, ast.Attribute):
        method = call.func.attr
        if method in {"read_text", "read_bytes", "iterdir", "glob", "rglob"} or (
            method == "open" and read_mode(argument(call, 0, "mode"))
        ):
            yield "read", value(call.func.value)
    if name in COMMAND_CALLS:
        command = argument(call, 0, "args", "command")
        if isinstance(command, (ast.List, ast.Tuple)):
            arguments = [
                "python" if qualified_name(item, aliases) == "sys.executable" else value(item)
                for item in command.elts
            ]
        else:
            raw = value(command)
            try:
                arguments = shlex.split(raw) if isinstance(raw, str) else []
            except ValueError:
                arguments = []
        target = command_target(arguments)
        if target:
            yield target


def scope_nodes(body):
    pending = deque(body)
    nodes = []
    while pending:
        node = pending.popleft()
        if isinstance(node, (ast.stmt, ast.expr)):
            nodes.append(node)
        if not isinstance(node, SCOPES):
            pending.extend(ast.iter_child_nodes(node))
    return sorted(nodes, key=lambda node: (node.lineno, node.col_offset))


def bind_values(root, source, package, node, values, aliases, module_globals):
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                values[target.id] = path_value(node.value, source, root, values, aliases)
    elif isinstance(node, ast.ImportFrom):
        inherited = module_globals(import_base(node, package))
        for entry in node.names:
            if entry.name in inherited:
                values[entry.asname or entry.name] = inherited[entry.name]
    elif isinstance(node, ast.Import):
        for entry in node.names:
            for name, value in module_globals(entry.name).items():
                values[f"{entry.asname or entry.name}.{name}"] = value


def bind_aliases(nodes, aliases):
    for node in nodes:
        if isinstance(node, ast.Import):
            aliases.update((entry.asname, entry.name) for entry in node.names if entry.asname)
        if isinstance(node, ast.ImportFrom) and node.module and not node.level:
            aliases.update(
                (entry.asname or entry.name, f"{node.module}.{entry.name}") for entry in node.names
            )


def scope_references(root, source, mappings, body, values, aliases, module_globals):
    nodes = scope_nodes(body)
    bind_aliases(nodes, aliases)
    package = module_package(source, mappings)
    for node in nodes:
        bind_values(root, source, package, node, values, aliases, module_globals)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for module in imports(node, package):
                for path in module_paths(root, mappings, module):
                    yield node.lineno, "import", path
        if isinstance(node, ast.Call):
            for kind, target in call_targets(node, source, root, values, aliases):
                if kind == "import":
                    paths = module_paths(root, mappings, target)
                else:
                    paths = local_paths(root, target)
                for path in paths:
                    yield node.lineno, kind, path
    for scope in (node for node in nodes if isinstance(node, SCOPES)):
        nested = [scope.body] if isinstance(scope, ast.Lambda) else scope.body
        locals_only = {
            node.id for node in scope_nodes(nested)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
        }
        if hasattr(scope, "args"):
            locals_only.update(node.arg for node in ast.iter_child_nodes(scope.args)
                               if isinstance(node, ast.arg))
        yield from scope_references(
            root, source, mappings, nested,
            {name: value for name, value in values.items() if name not in locals_only},
            {name: value for name, value in aliases.items() if name not in locals_only},
            module_globals,
        )


def module_value_reader(root, mappings):
    loading = set()

    @cache
    def from_source(source):
        loading.add(source)
        try:
            package = module_package(source, mappings)
            values = {"__file__": source}
            syntax = ast.parse(source.read_bytes(), filename=str(source))
            aliases = {}
            bind_aliases(syntax.body, aliases)
            for node in syntax.body:
                bind_values(root, source, package, node, values, aliases, from_module)
            return {
                name: value for name, value in values.items()
                if "." not in name and value is not None
            }
        finally:
            loading.remove(source)

    def from_module(name):
        for source in module_paths(root, mappings, name, include_parents=False):
            if source.suffix == ".py" and source not in loading:
                try:
                    return from_source(source)
                except (OSError, SyntaxError, ValueError):
                    # The direct source scan reports an unreadable core module.
                    return {}
        return {}

    return from_module


def dependency_target(root, path):
    lexical = Path(os.path.abspath(path))
    for candidate in (lexical, lexical.resolve()):
        if not candidate.is_relative_to(root):
            return candidate.as_posix()
        relative = candidate.relative_to(root)
        if not relative.parts or relative.parts[0] not in CORE:
            return relative.as_posix()
    return None


def experiment_code(root):
    def raise_error(error):
        raise error

    directory = root / "experiment"
    if not directory.exists() and not directory.is_symlink():
        return
    for current, dirs, files in os.walk(directory, onerror=raise_error):
        folder = Path(current)
        for name in dirs:
            link = folder / name
            if link.is_symlink() and any(
                link.resolve().is_relative_to(root / component) for component in CORE
            ):
                yield link.relative_to(root).as_posix()
        for name in files:
            path = folder / name
            if path.suffix.lower() in CODE_SUFFIXES or name in CODE_NAMES:
                yield path.relative_to(root).as_posix()
            elif not path.suffix and path.is_file() and not path.is_symlink():
                with path.open("rb") as stream:
                    if stream.read(2) == b"#!":
                        yield path.relative_to(root).as_posix()


def check(root):
    configuration = root / "pyproject.toml"
    settings = tomllib.loads(configuration.read_text()) if configuration.is_file() else {}
    package_dirs = settings.get("tool", {}).get("setuptools", {}).get("package-dir", {})
    mappings = [(name, (root / target).resolve()) for name, target in package_dirs.items()]
    mappings.sort(key=lambda entry: len(entry[0]), reverse=True)
    mappings.extend([("", root), ("", root / "src")])
    module_globals = module_value_reader(root, mappings)

    chain = {
        source: ()
        for name in sorted(CORE)
        for source in sorted((root / name).rglob("*.py"))
        if source.is_file()
    }
    pending = deque(chain)
    violations = set()
    errors = []
    while pending:
        source = pending.popleft()
        try:
            invalid_source = dependency_target(root, source)
            if invalid_source is not None:
                step = (source.relative_to(root).as_posix(), 1, "source", invalid_source)
                violations.add((*chain[source], step))
                continue
            syntax = ast.parse(source.read_bytes(), filename=str(source))
            for line, kind, path in scope_references(
                root, source, mappings, syntax.body, {"__file__": source}, {}, module_globals,
            ):
                forbidden = dependency_target(root, path)
                if forbidden is not None:
                    step = (source.relative_to(root).as_posix(), line, kind, forbidden)
                    violations.add((*chain[source], step))
                    continue
                resolved = path.resolve()
                if resolved.suffix == ".py" and resolved.is_file() and resolved not in chain:
                    step = (source.relative_to(root).as_posix(), line, kind,
                            resolved.relative_to(root).as_posix())
                    chain[resolved] = (*chain[source], step)
                    pending.append(resolved)
        except (OSError, RuntimeError, SyntaxError, ValueError) as error:
            errors.append(f"{source.relative_to(root)}: {error}")
    try:
        code = sorted(experiment_code(root))
    except (OSError, RuntimeError) as error:
        errors.append(f"experiment: {error}")
        code = []
    return sorted(violations), code, errors, len(chain)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Scientific project root catalogue")
    root = parser.parse_args().project.resolve()
    if not root.is_dir():
        parser.error(f"Project Directory does not exist {root}")
    try:
        violations, code, errors, scanned = check(root)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for chain in violations:
        print("Reliance on violations")
        for source, line, kind, target in chain:
            print(f"  {source}:{line} [{kind}] → {target}")
    for path in code:
        print(f"The lab catalogue contains code → {path}")
    for error in errors:
        print(f"Unable to check {error}", file=sys.stderr)
    print(
        f"Inspection {scanned} Core Python File, found {len(violations)} I’m relying on violations.,"
        f"{len(code)} An experimental catalogue code entry and {len(errors)} Error reading location."
    )
    if errors or not scanned:
        return 2
    return int(bool(violations or code))


if __name__ == "__main__":
    raise SystemExit(main())
