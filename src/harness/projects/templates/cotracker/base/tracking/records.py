"""Record effective tracking options, execution state, and readable result paths."""

from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f"{path.stem}_pending{path.suffix}")
    pending.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def read_tracking_run(directory):
    path = Path(directory) / "metadata" / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for relative in manifest["outputs"].values():
        if not (path.parent.parent / relative).is_file():
            raise ValueError(f"Declared result is missing: {relative}")
    return manifest


class TrackingRun:
    """Write one manifest per execution with stable relative output paths."""

    def __init__(self, workspace, configuration):
        self.configuration = configuration
        self.directory = workspace.joinpath(
            "experiment", configuration["dataset"], configuration["model"],
            configuration["task"], configuration["subname"],
        )
        if self.directory.resolve() != self.directory:
            raise ValueError(f"Choose a regular experiment path within {workspace}")
        self.directory.mkdir(parents=True, exist_ok=False)
        self.manifest = {
            "schema_version": 1,
            "project_id": "cotracker_research",
            "run_id": str(uuid4()),
            "task": configuration["task"],
            "subname": configuration["subname"],
            "configuration": configuration,
            "effective_config": "metadata/config.json",
            "formal_started": False,
            "inputs": {
                "video": configuration["video"],
                "checkpoint": configuration["checkpoint"],
            },
            "source": {"distribution": "cotracker", "version": "3.0"},
            "outputs": {},
            "diagnostics": [],
        }
        write_json(self.directory / "metadata" / "config.json", configuration)
        self.write("running")

    def write(self, status, **fields):
        self.manifest.update(status=status, updated_at=datetime.now(timezone.utc).isoformat(), **fields)
        write_json(self.directory / "metadata" / "manifest.json", self.manifest)
