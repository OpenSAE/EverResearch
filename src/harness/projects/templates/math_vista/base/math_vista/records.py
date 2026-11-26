"""Save MathVista configuration and results for runs using the standard paths."""

from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from filelock import FileLock

from mathvista.runtime import dataset_path, project_root
from utilities import save_json


@contextmanager
def run_record(directory, task, split, purpose, effective, *, standard):
    if not standard:
        yield lambda report, **kwargs: None
        return

    locks = project_root() / ".everresearch" / "run_locks"
    locks.mkdir(parents=True, exist_ok=True)
    with FileLock(locks / f"{split}-{task}-{purpose}.lock"):
        with standard_run(directory, task, split, purpose, effective) as record:
            yield record


@contextmanager
def standard_run(directory, task, split, purpose, effective):
    artifacts = directory
    root = artifacts.parent
    artifacts.mkdir(parents=True, exist_ok=True)
    effective = {"dataset": dataset_path(split), "task": task, **effective}
    save_json(effective, root / "config.json")
    manifest = {
        "run_id": str(uuid4()),
        "task": task,
        "subname": purpose,
        "status": "running",
        "effective_config": "config.json",
        "formal_started": False,
        "outputs": {},
    }

    def update(status):
        manifest["status"] = status
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        manifest["outputs"] = {
            path.stem: path.relative_to(root).as_posix()
            for group in ("artifacts", "reports")
            for path in (root / group).glob("*.json")
        }
        save_json(manifest, root / "manifest.json")

    def record_precheck(report, *, formal_started=True):
        (root / "reports").mkdir(exist_ok=True)
        save_json(report, root / "reports/precheck.json")
        manifest["precheck_seconds"] = report["seconds"]
        manifest["formal_started"] = formal_started

    update("running")
    try:
        yield record_precheck
    except BaseException as error:
        stage = "task" if manifest["formal_started"] else "automatic_precheck"
        manifest["diagnostics"] = [{"stage": stage, "message": str(error) or type(error).__name__}]
        update("failed")
        raise
    else:
        update("succeeded")
