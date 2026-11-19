"""目的：记录运行身份、实测环境、状态以及可读取的产物位置。

适用范围：训练、预检和比较的运行清单与报告。
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from uuid import uuid4

from omegaconf import OmegaConf

from .environment import snapshot


def now():
    return datetime.now(timezone.utc).isoformat()


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".writing")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def normalize_subname(value):
    name = re.sub(r"[-_ ]", "_", value.strip()).lower()
    word = r"[^\W\d_][^\W_]*"
    if not re.fullmatch(rf"{word}(?:_{word}){{0,2}}", name):
        raise ValueError("实验名称须用一至三个描述用途的词，以空格、下划线或连字符分隔")
    return name


def experiment_root():
    checkout = Path(__file__).resolve().parents[2]
    cwd = Path.cwd().resolve()
    for parent in (checkout, cwd, *cwd.parents):
        if (parent / "pyproject.toml").is_file() and (parent / "cub_template/cli.py").is_file():
            return parent / "experiment"
    raise ValueError("请从 CUB 模板的项目目录运行，以定位项目一级目录 experiment/")


class Run:
    def __init__(self, operation, config_path, subname, *, components=None):
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        groups = components if components is not None else ("unresolved",)
        output = experiment_root()
        subname = normalize_subname(subname)
        self.root = output.joinpath(*groups, subname, name)
        if self.root.resolve() != self.root:
            raise ValueError(f"实验目录须位于项目内的实际路径：{self.root}")
        self.root.mkdir(parents=True, exist_ok=False)
        from .. import datasets, models, tasks

        package = Path(__file__).resolve().parents[1]
        component_roots = {
            name: Path(module.__file__).resolve().parent
            for name, module in (("datasets", datasets), ("models", models), ("tasks", tasks))
        }
        source_roots = {"cub_template": package, **component_roots}
        sources = {
            f"{name}/{path.relative_to(root).as_posix()}": hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for name, root in source_roots.items()
            for path in sorted(root.rglob("*.py"))
            if name != "cub_template"
            or not any(path.is_relative_to(c) for c in component_roots.values())
        }
        self.manifest = {
            "schema_version": 1,
            "project_id": "cub_reference",
            "run_id": name,
            "subname": subname,
            "task": components[-1] if components else None,
            "operation": operation,
            "status": "running",
            "inputs": {},
            "configuration": None,
            "source": {"python_sha256": sources},
            "config_file": str(Path(config_path).resolve()),
            "environment": snapshot(None),
            "outputs": {},
            "diagnostics": [],
        }
        self.save()

    def save(self, status=None):
        if status is not None:
            self.manifest["status"] = status
        self.manifest["updated_at"] = now()
        write_json(self.root / "metadata/manifest.json", self.manifest)

    def record_configuration(self, config):
        relative = "config.yaml"
        header = (
            "# 目的和主要功能：保存本次运行实际使用的配置。\n"
            "# 适用范围：同目录的报告、权重与运行清单。\n"
        )
        write_text(self.root / relative, header + OmegaConf.to_yaml(config))
        self.manifest["configuration"] = config
        self.manifest["effective_config"] = relative

    def report(self, role, content):
        relative = f"reports/{role}.json"
        write_json(self.root / relative, content)
        self.manifest["outputs"][role] = relative
        self.save()
