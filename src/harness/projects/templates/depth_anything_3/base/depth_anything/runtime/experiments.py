"""Plan and record repeatable local CLI inference runs.

The CLI calls these functions after resolving its input and model options.
Each named experiment groups separate executions with readable manifests.
"""

import json
import platform
import re
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from omegaconf import OmegaConf

from .paths import CONFIG_ROOT, find_checkout


_active_execution = ContextVar("active_execution", default=None)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "unnamed"


def experiment_directory(input_path: str, model: str, name: str) -> Path:
    """Return the stable location for a named inference experiment."""
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", name) or name in {
        "run", "test", "output", "results", "experiment", "default", "trial"
    }:
        raise ValueError("Use one to three lowercase words describing the purpose, e.g. scene_geometry")

    root = find_checkout()
    if root is None:
        raise ValueError(
            "Run named experiments from a Depth Anything checkout or use "
            "--export-dir to export to an explicit location"
        )
    source = Path(input_path).resolve()
    source_name = _slug(source.stem if source.is_file() else source.name)
    model_name = _slug(Path(model).name)
    catalogs = OmegaConf.load(CONFIG_ROOT / "config.yaml").catalogs
    registered_input = catalogs.dataset.get(source_name)
    dataset = (
        source_name if registered_input and (root / registered_input).resolve() == source
        else "media"
    )
    registered_model = model_name if model_name in catalogs.model else "local_model"
    return root / "experiment" / dataset / registered_model / "inference" / name



def _write_json(path: Path, data: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def describe_artifacts(execution: Path) -> dict:
    """Preserve normal export paths and bundle frame series with original member names."""
    artifacts = execution / "artifacts"
    preview = artifacts / "scene.jpg"
    if preview.is_file() and (artifacts / "scene.glb").is_file():
        preview.rename(artifacts / "scene_preview.jpg")

    files = sorted(path for path in artifacts.rglob("*") if path.is_file())
    named = {}
    series = []
    for path in files:
        if re.fullmatch(r"[a-z]+(?:_[a-z]+)*", path.stem) and path.stem not in named:
            named[path.stem] = path.relative_to(execution).as_posix()
        else:
            series.append(path)
    if series:
        bundle = artifacts / "frame_previews.zip"
        if bundle.exists():
            raise FileExistsError(f"Export name reserved for numbered frame files: {bundle}")
        with ZipFile(bundle, "w", compression=ZIP_DEFLATED) as archive:
            for path in series:
                archive.write(path, path.relative_to(artifacts).as_posix())
        for path in series:
            path.unlink()
        named[bundle.stem] = bundle.relative_to(execution).as_posix()
    return named


@contextmanager
def record_precheck(samples_checked=None):
    """Record rejection at any precheck stage and success after the bounded probe."""
    active = _active_execution.get()
    try:
        yield active is not None
    except Exception as error:
        if active is not None:
            _, manifest, _ = active
            manifest["diagnostics"] = [
                {"stage": "automatic_precheck", "message": str(error) or type(error).__name__}
            ]
        raise
    if active is not None and samples_checked is not None:
        execution, manifest, started = active
        report = execution / "reports" / "precheck.json"
        report.parent.mkdir(exist_ok=True)
        _write_json(report, {"samples_checked": samples_checked})
        manifest["outputs"]["precheck"] = "reports/precheck.json"
        manifest["precheck_seconds"] = perf_counter() - started
        manifest["formal_started"] = True


@contextmanager
def record_execution(directory: Path, config: dict):
    """Record an execution and yield its export directory."""
    entry_timer = perf_counter()
    started = datetime.now(timezone.utc)
    run_id = started.strftime("%Y%m%dT%H%M%S.%fZ") + "-" + uuid4().hex
    execution = directory / "executions" / run_id
    execution.mkdir(parents=True)
    config.update(component_paths={
        "dataset": directory.parent.parent.parent.name,
        "model": directory.parent.parent.name,
        "task": directory.parent.name,
    })
    config_path = execution / "config.json"
    _write_json(config_path, config)

    manifest_path = execution / "manifest.json"
    manifest = {
        "execution_id": run_id,
        "run_id": run_id,
        "subname": directory.name,
        "task": directory.parent.name,
        "started_at": started.isoformat(),
        "status": "running",
        "config": "config.json",
        "effective_config": "config.json",
        "environment": {"python": sys.executable, "python_version": platform.python_version()},
        "formal_started": False,
        "artifacts": [],
        "outputs": {},
    }
    _write_json(manifest_path, manifest)

    artifacts = execution / "artifacts"
    artifacts.mkdir()
    token = _active_execution.set((execution, manifest, entry_timer))
    try:
        yield artifacts
        outputs = describe_artifacts(execution)
        if not outputs:
            raise RuntimeError("The export did not produce any recorded artifacts")
        manifest["outputs"].update(outputs)
        manifest["status"] = "succeeded"
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["error"] = str(exc) or type(exc).__name__
        try:
            manifest["outputs"].update(describe_artifacts(execution))
        except Exception as recording_error:
            manifest["recording_error"] = str(recording_error)
        raise
    finally:
        _active_execution.reset(token)
        _write_json(config_path, config)
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        manifest["artifacts"] = sorted(
            output for output in manifest["outputs"].values() if output.startswith("artifacts/")
        )
        _write_json(manifest_path, manifest)


def read_executions(directory: Path) -> list:
    """Read the manifests for a named experiment in start-time order."""
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (directory / "executions").glob("*/manifest.json")
    ]
    return sorted(records, key=lambda record: record["started_at"])
