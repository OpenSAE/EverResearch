"""Purpose: Recording of operational identity, measured environment, state and the location of accessible products.

Scope of application: Operational inventory and reporting for training, precheck and comparison.
"""

from datetime import datetime, timezone
import hashlib
from itertools import count
import json
from pathlib import Path
import re
from uuid import uuid4

from omegaconf import OmegaConf

from .environment import snapshot


MODEL_PATHS = {
    "resnet18_mlp": "residual_classifier",
    "resnet18_mlp_small": "residual_classifier_small",
}
DIGIT_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


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
        raise ValueError("The name of the experiment shall be separated by one to three words describing the purpose by space, underlined or hyphenation")
    return name


def experiment_root():
    checkout = Path(__file__).resolve().parents[3]
    cwd = Path.cwd().resolve()
    for parent in (checkout, cwd, *cwd.parents):
        if (parent / "pyproject.toml").is_file() and (parent / "base/cub_template/command.py").is_file():
            return parent / "experiment"
    raise ValueError("From CUB Template project directories run to locate project level I directories experiment/")


class Run:
    def __init__(self, operation, config_path, subname, *, components):
        dataset, model, task = components
        model_path = MODEL_PATHS.get(model, model)
        output = experiment_root()
        subname = normalize_subname(subname)
        folder = output / dataset / model_path / task / subname
        if folder.resolve() != folder:
            raise ValueError(f"The experiment directory must be a real path within the project: {folder}")
        for number in count(1):
            sequence = "_".join(DIGIT_WORDS[int(digit)] for digit in str(number))
            execution_name = f"{operation}_execution_{sequence}"
            self.root = folder / execution_name
            try:
                self.root.mkdir(parents=True)
                break
            except FileExistsError:
                continue
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
            "run_id": uuid4().hex,
            "execution_name": execution_name,
            "subname": subname,
            "task": task,
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
        model = config["model"]["name"]
        if model in MODEL_PATHS:
            config.setdefault("component_paths", {})["model"] = MODEL_PATHS[model]
        relative = "config.yaml"
        header = (
            "# Purpose and main function: to save the configuration actually used for this operation.\n"
            "# Scope of application: List of reports, weights and operations in the same directory.\n"
        )
        write_text(self.root / relative, header + OmegaConf.to_yaml(config))
        self.manifest["configuration"] = config
        self.manifest["effective_config"] = relative

    def report(self, role, content):
        relative = f"reports/{role}.json"
        write_json(self.root / relative, content)
        self.manifest["outputs"][role] = relative
        self.save()
