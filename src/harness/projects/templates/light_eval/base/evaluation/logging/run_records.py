"""Persist evaluation runs and locate their archived response details."""

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from uuid import uuid4


@contextmanager
def staged_run(study: Path):
    """Publish a completed run in one rename, with any failed write kept out of view.

    Yields:
        An unpublished execution directory with its artifact directory created.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_id = f"{timestamp}-{uuid4().hex[:12]}"
    executions = study / "executions"
    executions.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".writing-", dir=executions) as staging:
        run = Path(staging) / run_id
        (run / "artifacts").mkdir(parents=True)
        yield run
        run.rename(executions / run_id)


def detail_names(task_names):
    """Build stable distinct artifact names for the tasks in one evaluation.

    Yields:
        The original task ID and a unique artifact name.
    """
    for index, task in enumerate(task_names):
        # An alphabetical suffix keeps artifact names independent of task spelling.
        suffix = ""
        while index >= 0:
            suffix = chr(ord("a") + index % 26) + suffix
            index = index // 26 - 1
        yield task, f"responses_{suffix}"


def write_manifest(
    run: Path, encode, results: dict, response_paths: dict[str, str], date_id: str, subname: str
) -> None:
    """Store effective configuration and publish the completed run to readers."""
    component_paths = results["component_paths"]
    config = {
        "component_paths": component_paths,
        "evaluation": results["config_general"],
        "tasks": results["config_tasks"],
    }
    (run / "config.json").write_text(encode(config), encoding="utf-8")
    outputs = {"scores": "artifacts/scores.json"}
    outputs.update({Path(path).stem: path for path in response_paths.values()})
    manifest = {
        "run_id": run.name,
        "source_date_id": date_id,
        "subname": subname,
        "task": component_paths["task"],
        "status": "succeeded",
        "effective_config": "config.json",
        "outputs": outputs,
        "response_details": response_paths,
    }
    temporary = run / ".manifest.tmp"
    temporary.write_text(encode(manifest), encoding="utf-8")
    temporary.replace(run / "manifest.json")


def recorded_details(study: Path):
    """Yield the original date, run path and exact task-to-artifact map."""
    for manifest_file in (study / "executions").glob("*/manifest.json"):
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            if manifest["status"] == "succeeded":
                responses = {}
                for task, value in manifest["response_details"].items():
                    relative = PurePosixPath(value)
                    if len(relative.parts) == 2 and relative.parts[0] == "artifacts" and relative.suffix == ".parquet":
                        path = manifest_file.parent / relative
                        if path.is_file() and path.resolve().is_relative_to(manifest_file.parent.resolve()):
                            responses[task] = str(relative)
                if responses:
                    yield manifest["source_date_id"], manifest_file.parent, responses
        except (OSError, ValueError, KeyError, AttributeError, TypeError):
            continue
