"""Save your own data directories and Python Enter and use these options to start the original project command.

For visible registration or search of home resources, installation project dependence and startup specified by the caller Python Command.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from ..central import ProjectError, identity
from ..core.workspace import save


DATA_REFERENCE = re.compile(r"\{data:([a-z0-9][a-z0-9_-]{0,79})\}")


def binding_path(harness, project_id):
    return harness.resolve(f"src/project/{identity(project_id)}/resources.json")


def stored_bindings(harness, project_id):
    path = binding_path(harness, project_id)
    return json.loads(path.read_text()) if path.exists() else {"data": {}, "python": None}


def read(harness, project_id):
    bindings = stored_bindings(harness, project_id)
    python = bindings["python"]
    return {
        "data": {name: str(harness.bound_path(path)) for name, path in bindings["data"].items()},
        "python": str(harness.bound_path(python)) if python is not None else None,
    }


def data_directory(root, value):
    path = (root / Path(value).expanduser()).resolve(strict=True)
    if not path.is_dir():
        raise ProjectError(f"Data path should point to directory:{path}")
    return str(path)


def interpreter(root, value):
    # Keep the executable's symlink spelling so Python discovers its virtual environment.
    path = Path(os.path.abspath(root / Path(value).expanduser()))
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ProjectError(f"Python Path should point to the executable:{path}")
    return str(path)


def update(harness, project_id, *, data=(), remove_data=(), python=None, clear_python=False):
    root = harness.project_root(project_id)
    target = binding_path(harness, project_id)
    bindings = stored_bindings(harness, project_id)
    for entry in data:
        name, separator, path = entry.partition("=")
        if not separator or not path:
            raise ProjectError("Data binding uses name=path")
        bindings["data"][identity(name)] = harness.store_path(Path(data_directory(root, path)))
    for name in remove_data:
        bindings["data"].pop(identity(name), None)
    if python is not None:
        bindings["python"] = harness.store_path(Path(interpreter(root, python)))
    elif clear_python:
        bindings["python"] = None
    save(target, bindings, source=__file__)
    return read(harness, project_id)


def install(harness, project_id, requirements, *, preserve_packages=()):
    root = harness.project_root(project_id)
    python = read(harness, project_id)["python"]
    if python is None:
        raise ProjectError(f"After you. {project_id} Tie down the engine. Python")
    python = interpreter(root, python)
    manifest = (root / Path(requirements).expanduser()).resolve()
    if not manifest.is_file():
        raise ProjectError(f"Could not find dependency list:{manifest}")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) for name in preserve_packages):
        raise ProjectError("--preserve-package Use installed Python Release Package Name")

    parent = harness.resolve(".workspace/harness/projects/install")
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"environment_install_{project_id}_", dir=parent) as scratch:
        environment = {**os.environ, "TMPDIR": scratch, "TEMP": scratch, "TMP": scratch}
        command = [python, "-m", "pip", "install", "--no-cache-dir", "-r", str(manifest)]
        if preserve_packages:
            lookup = "import sys\nfrom importlib.metadata import version\nfor name in sys.argv[1:]: print(version(name))"
            installed = subprocess.run(
                [python, "-I", "-c", lookup, *preserve_packages], cwd=root,
                env=environment, capture_output=True, text=True,
            )
            if installed.returncode:
                raise ProjectError(
                    f"Please choose first. Python Installing packages to keep:{', '.join(preserve_packages)}"
                )
            constraints = Path(scratch) / "constraints.txt"
            constraints.write_text(
                "".join(
                    f"{name}=={version}\n"
                    for name, version in zip(preserve_packages, installed.stdout.splitlines(), strict=True)
                ),
                encoding="utf-8",
            )
            command.extend(["--constraint", str(constraints)])
        child = subprocess.run(command, cwd=root, env=environment)
    return child.returncode if child.returncode >= 0 else 128 - child.returncode


def run(harness, project_id, arguments, *, environment=()):
    root = harness.project_root(project_id)
    bindings = read(harness, project_id)
    if bindings["python"] is None:
        raise ProjectError(f"After you. {project_id} Tie down the engine. Python")
    if not arguments:
        raise ProjectError("Yes, please. -- Projects to be made available Python Start Parameters")

    def replace(match):
        name = match[1]
        if name not in bindings["data"]:
            raise ProjectError(f"{project_id} Data directory not yet bound {name}")
        return data_directory(root, bindings["data"][name])

    expanded = [DATA_REFERENCE.sub(replace, value) for value in arguments]
    process_environment = os.environ.copy()
    for assignment in environment:
        name, separator, value = assignment.partition("=")
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ProjectError("Use of environment variables NAME=VALUE")
        process_environment[name] = DATA_REFERENCE.sub(replace, value)
    child = subprocess.run([interpreter(root, bindings["python"]), *expanded], cwd=root,
                           env=process_environment)
    return child.returncode if child.returncode >= 0 else 128 - child.returncode
