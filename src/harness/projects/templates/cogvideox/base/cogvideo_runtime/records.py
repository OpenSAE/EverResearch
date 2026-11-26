"""Save and reopen CogVideoX generation configurations, manifests and MP4 artifacts."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from uuid import uuid4


RESERVED_NAMES = {"run", "trial", "experiment", "default", "output", "test", "job", "untitled"}


def publish_generation(workspace, purpose, execution, effective, generate):
    """Create one generation record and keep unfinished video writes outside artifacts."""
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", purpose) or purpose in RESERVED_NAMES:
        raise ValueError("Use one to three lowercase words for --purpose.")
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+)*", execution) or execution in RESERVED_NAMES | {
        "artifacts", "reports", "logs", "metadata", "tmp", "executions",
    }:
        raise ValueError("Use a descriptive name for --execution.")
    parts = effective["component_paths"]
    run = (workspace / "experiment" / parts["dataset"] / parts["model"] / parts["task"]
           / purpose / "executions" / execution)
    run.mkdir(parents=True)
    (run / "metadata").mkdir()
    (run / "tmp").mkdir()
    manifest_path = run / "metadata" / "manifest.json"
    config_path = run / "config.json"
    manifest = {
        "run_id": str(uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "subname": purpose,
        "execution_name": execution,
        "task": parts["task"],
        "command": sys.argv,
        "status": "running",
        "effective_config": "config.json",
        "outputs": {},
    }
    config_path.write_text(json.dumps(effective, indent=2) + "\n", encoding="utf-8")

    def save_manifest():
        staged = run / "metadata" / ".manifest.json"
        staged.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        staged.replace(manifest_path)

    save_manifest()
    staged_video = run / "tmp" / "generated_video.mp4"
    output = run / "artifacts" / "generated_video.mp4"
    try:
        generate(staged_video)
        output.parent.mkdir()
        staged_video.replace(output)
    except BaseException as error:
        manifest.update(status="interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
                        error=f"{type(error).__name__}: {error}")
        raise
    else:
        manifest.update(status="succeeded", outputs={"generated_video": "artifacts/generated_video.mp4"})
    finally:
        manifest["ended_at"] = datetime.now(timezone.utc).isoformat()
        save_manifest()
    return run


def read_generation(run: Path):
    """Open the saved manifest and the exact configuration selected by that run."""
    manifest = json.loads((run / "metadata" / "manifest.json").read_text(encoding="utf-8"))
    config = json.loads((run / manifest["effective_config"]).read_text(encoding="utf-8"))
    return {"run": str(run.resolve()), "manifest": manifest, "configuration": config}
