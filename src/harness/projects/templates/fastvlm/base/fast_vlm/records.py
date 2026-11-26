"""Write and read per-run FastVLM image-prompt predictions and their manifests."""
import errno
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from itertools import count
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

TASK = "image_prompt"
_GENERIC_NAMES = {"default", "experiment", "job", "output", "run", "test", "trial", "untitled"}
_RELEASE_CHECKPOINT = re.compile(r"llava-fastvithd_(0\.5b|1\.5b|7b)_stage([23])")
_DIGIT_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


def valid_subname(value):
    return bool(re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", value)) and value not in _GENERIC_NAMES


def valid_dataset(value):
    return bool(re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", value))


def _write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _revision(root):
    if not (root / ".git").exists():
        return None
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _versions():
    versions = {}
    for package in ("torch", "transformers", "Pillow"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def _model_directory(model_path):
    release = _RELEASE_CHECKPOINT.fullmatch(model_path.name.lower())
    if release:
        size, stage = release.groups()
        variant = {"0.5b": "small", "1.5b": "medium", "7b": "large"}[size]
        return f"fast_vision_{variant}_stage{stage}"
    return "fast_vision"


def component_paths(config):
    dataset = config["dataset"]
    return {
        "dataset": dataset if dataset == "coco_val" else "user_image",
        "model": _model_directory(Path(config["model_path"])),
        "task": TASK,
    }


def save_result(root, config, input_info, answer, *, precheck=None, precheck_error=None, precheck_seconds=None):
    if not valid_dataset(config["dataset"]):
        raise ValueError(f'Invalid dataset name: {config["dataset"]!r}')
    if not valid_subname(config["subname"]):
        raise ValueError(f'Invalid experiment name: {config["subname"]!r}')

    updated_at = datetime.now(timezone.utc)
    run_id = f'{updated_at:%Y%m%dT%H%M%SZ}-{uuid4().hex}'
    paths = component_paths(config)
    group = root / "experiment" / paths["dataset"] / paths["model"] / TASK / config["subname"] / "executions"
    group.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".pending-", dir=group) as temporary:
        stage = Path(temporary) / "result"
        (stage / "metadata").mkdir(parents=True)
        _write_json(stage / "config.json", {**config, "component_paths": paths})
        outputs = {}
        if precheck_error is None:
            outputs["prediction"] = "artifacts/prediction.json"
            (stage / "artifacts").mkdir()
            _write_json(stage / outputs["prediction"], {"input": input_info, "answer": answer})
        if precheck is not None:
            outputs["precheck"] = "reports/precheck.json"
            (stage / "reports").mkdir()
            _write_json(stage / outputs["precheck"], precheck)
        manifest = {
            "schema_version": 2,
            "project_id": "fastvlm",
            "run_id": run_id,
            "subname": config["subname"],
            "task": TASK,
            "status": "succeeded" if precheck_error is None else "failed",
            "updated_at": updated_at.isoformat(),
            "inputs": {"image": input_info, "checkpoint": config["model_path"], "base": config["model_base"]},
            "effective_config": "config.json",
            "source": {"revision": _revision(root)},
            "environment": {"python": sys.executable, "device": config["device"], "versions": _versions()},
            "outputs": outputs,
        }
        if precheck_seconds is not None:
            manifest["precheck_seconds"] = precheck_seconds
            manifest["formal_started"] = precheck_error is None
        if precheck_error is not None:
            manifest["diagnostics"] = [{"stage": "automatic_precheck", "message": precheck_error}]
        _write_json(stage / "metadata/manifest.json", manifest)
        for number in count(1):
            sequence = "_".join(_DIGIT_WORDS[int(digit)] for digit in str(number))
            run_path = group / f"prediction_execution_{sequence}"
            if run_path.exists():
                continue
            try:
                stage.rename(run_path)
                break
            except OSError as error:
                if error.errno not in (errno.EEXIST, errno.ENOTEMPTY):
                    raise
    return run_path / "metadata/manifest.json"


def read_result(manifest_path):
    manifest_path = Path(manifest_path).expanduser()
    if not manifest_path.exists():
        manifest_path = _legacy_manifest(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("project_id"), manifest.get("task")) != ("fastvlm", TASK) or manifest.get("schema_version") not in (1, 2):
        raise ValueError(f"Unsupported FastVLM manifest: {manifest_path}")
    if manifest.get("status") != "succeeded":
        raise ValueError(f"FastVLM run has no prediction: {manifest.get('status')}")
    run_root = manifest_path.resolve().parent.parent
    prediction = (run_root / manifest["outputs"]["prediction"]).resolve()
    if run_root not in prediction.parents:
        raise ValueError("Prediction path must be inside the run directory.")
    return json.loads(prediction.read_text(encoding="utf-8"))


def _legacy_manifest(path):
    if len(path.parts) < 4 or path.parts[-4] != "runs" or path.parts[-2:] != ("metadata", "manifest.json"):
        return path
    run_id = path.parts[-3]
    if re.fullmatch(r"[a-f0-9]{32}", run_id) is None:
        return path
    experiment = next((parent for parent in path.resolve().parents if parent.name == "experiment"), None)
    if experiment is None:
        return path
    matches = list(experiment.glob(f"**/executions/*-{run_id}/metadata/manifest.json"))
    return matches[0] if len(matches) == 1 else path
