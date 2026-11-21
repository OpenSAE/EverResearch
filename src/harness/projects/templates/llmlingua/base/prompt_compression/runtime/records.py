"""Store batch compression results and their effective configuration."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from ..version import VERSION
from .config import dataset_path, find_checkout, load_defaults, source_checkout


def model_path(model_name):
    for name, details in load_defaults()["catalogs"]["model"].items():
        if details.get("checkpoint") == model_name:
            return name

    model = model_name.rstrip("/\\").replace("\\", "/")
    publisher, _, checkpoint = model.rpartition("/")
    if publisher == "microsoft" and checkpoint.lower().startswith("llmlingua-2-"):
        name = checkpoint
    elif re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", publisher):
        name = f"{publisher}_{checkpoint}"
    else:
        name = checkpoint
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "local_model"


def component_paths(config):
    return {
        "dataset": dataset_path(config["dataset"]),
        "model": model_path(config["model_name"]),
        "task": "compression",
    }


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, indent=4, ensure_ascii=False)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def experiment_root():
    checkout = source_checkout() or find_checkout(Path.cwd())
    return checkout / "experiment" if checkout else None


def run_directory(config, root):
    now = datetime.now(timezone.utc)
    run_id = f"{now:%Y%m%dT%H%M%S.%fZ}-{uuid4().hex[:8]}"
    paths = component_paths(config)
    return root.joinpath(
        paths["dataset"], paths["model"], paths["task"], config["name"],
        "executions", run_id,
    )


def manifest_path(run):
    return run / "metadata" / "manifest.json"


def initialize_run(run, config):
    run.mkdir(parents=True, exist_ok=False)
    manifest = {
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config": "config.json",
        "effective_config": "config.json",
        "run_id": run.name,
        "subname": config["name"],
        "task": "compression",
        "outputs": {},
        "artifact": "artifacts/compressed_prompts.json",
        "llmlingua_version": VERSION,
        "python_version": sys.version.split()[0],
    }
    write_json(run / manifest["config"], dict(config, component_paths=component_paths(config)))
    write_json(manifest_path(run), manifest)
    return manifest


def read_run(run):
    run = run.resolve()
    if not manifest_path(run).is_file():
        # Older links placed the execution ID directly under the named purpose.
        parts = run.parts
        if "experiment" in parts:
            index = len(parts) - 1 - tuple(reversed(parts)).index("experiment")
            root = Path(*parts[:index + 1])
            remainder = parts[index + 1:]
            if len(remainder) in {5, 6}:
                dataset, *model, task, purpose, run_id = remainder
                model_name = "_".join(model)
                if model_name.startswith("microsoft_llmlingua_2_"):
                    model_name = model_name[len("microsoft_"):]
                if model_name.startswith("llmlingua_2_"):
                    model = [model_name]
                run = root.joinpath(
                    dataset_path(dataset), *model, task, purpose,
                    "executions", run_id,
                )
    with manifest_path(run).open(encoding="utf-8") as stream:
        manifest = json.load(stream)
    if manifest["status"] == "succeeded":
        manifest["status"] = "completed"
    record = {"manifest": manifest}
    for key in ("config", "artifact"):
        path = (run / manifest[key]).resolve()
        if run not in path.parents:
            raise ValueError(f"Manifest {key} must point inside the run directory.")
        if key == "config" or manifest["status"] == "completed" or path.is_file():
            with path.open(encoding="utf-8") as stream:
                record[key] = json.load(stream)
    return record
