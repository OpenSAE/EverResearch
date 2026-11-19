"""为各项目保存本机数据目录与 Python 入口，并使用这些选择启动原项目命令。

用于显式登记或查询本机资源，以及运行由调用方指定的 Python 参数。
"""

import json
import os
from pathlib import Path
import re
import subprocess

from ..central import ProjectError, identity
from ..core.workspace import save, update_lock


DATA_REFERENCE = re.compile(r"\{data:([a-z0-9][a-z0-9_-]{0,79})\}")


def binding_path(harness, project_id):
    return harness.resolve(f".workspace/harness/projects/resources/bindings_{identity(project_id)}.json")


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
        raise ProjectError(f"数据路径应指向目录：{path}")
    return str(path)


def interpreter(root, value):
    # Keep the executable's symlink spelling so Python discovers its virtual environment.
    path = Path(os.path.abspath(root / Path(value).expanduser()))
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ProjectError(f"Python 路径应指向可执行文件：{path}")
    return str(path)


def update(harness, project_id, *, data=(), remove_data=(), python=None, clear_python=False):
    root = harness.project_root(project_id)
    target = binding_path(harness, project_id)
    with update_lock(target):
        bindings = stored_bindings(harness, project_id)
        for entry in data:
            name, separator, path = entry.partition("=")
            if not separator or not path:
                raise ProjectError("数据绑定使用 名称=路径")
            bindings["data"][identity(name)] = harness.store_path(Path(data_directory(root, path)))
        for name in remove_data:
            bindings["data"].pop(identity(name), None)
        if python is not None:
            bindings["python"] = harness.store_path(Path(interpreter(root, python)))
        elif clear_python:
            bindings["python"] = None
        save(target, bindings, source=__file__)
    return read(harness, project_id)


def run(harness, project_id, arguments, *, environment=()):
    root = harness.project_root(project_id)
    bindings = read(harness, project_id)
    if bindings["python"] is None:
        raise ProjectError(f"请先为 {project_id} 绑定本机 Python")
    if not arguments:
        raise ProjectError("请在 -- 后提供项目的 Python 启动参数")

    def replace(match):
        name = match[1]
        if name not in bindings["data"]:
            raise ProjectError(f"{project_id} 尚未绑定数据目录 {name}")
        return data_directory(root, bindings["data"][name])

    expanded = [DATA_REFERENCE.sub(replace, value) for value in arguments]
    process_environment = os.environ.copy()
    for assignment in environment:
        name, separator, value = assignment.partition("=")
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ProjectError("环境变量使用 NAME=VALUE")
        process_environment[name] = DATA_REFERENCE.sub(replace, value)
    child = subprocess.run([interpreter(root, bindings["python"]), *expanded], cwd=root,
                           env=process_environment)
    return child.returncode if child.returncode >= 0 else 128 - child.returncode
