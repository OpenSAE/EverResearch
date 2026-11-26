"""Save and read recorded speech experiments through the Whisper command."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .utils import get_writer


def write_json(path, data):
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def read_experiment(directory):
    """Find a recorded run's status, effective configuration, and result files."""
    directory = Path(directory)
    manifest = json.loads(
        (directory / "metadata" / "manifest.json").read_text(encoding="utf-8")
    )
    configuration = json.loads(
        (directory / manifest["effective_config"]).read_text(encoding="utf-8")
    )
    return {"manifest": manifest, "configuration": configuration}


def experiment_directory(project_root, purpose):
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", purpose) or purpose in {
        "run",
        "trial",
        "experiment",
        "default",
        "output",
        "test",
        "job",
        "untitled",
    }:
        raise ValueError(
            "Choose one to three descriptive words joined by underscores for --experiment"
        )
    root = Path(project_root).resolve()
    if (
        not (root / "conf" / "config.json").is_file()
        or not (root / "base" / "whisper").is_dir()
    ):
        raise ValueError("Point --project-root to the WhisperResearch checkout")
    return root / "experiment" / "audio" / "whisper" / "speech" / purpose


class Experiment:
    """Record one input and keep all output paths relative to the run directory."""

    def __init__(self, directory, configuration):
        self.directory = directory
        self.manifest_path = directory / "metadata" / "manifest.json"
        self.manifest = {
            "run_id": uuid4().hex,
            "subname": directory.name,
            "task": "speech",
            "status": "running",
            "effective_config": "config.json",
            "formal_started": False,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "command": sys.argv,
            "outputs": {},
            "diagnostics": [],
        }
        directory.mkdir(parents=True)
        self.manifest_path.parent.mkdir()
        write_json(directory / "config.json", configuration)
        write_json(self.manifest_path, self.manifest)

    def save_precheck(self, elapsed, report=None):
        self.manifest["precheck_seconds"] = elapsed
        if report is not None:
            location = self.directory / "reports" / "precheck.json"
            location.parent.mkdir()
            write_json(location, report)
            self.manifest["outputs"]["precheck"] = "reports/precheck.json"
        write_json(self.manifest_path, self.manifest)

    def start(self):
        self.manifest["formal_started"] = True
        write_json(self.manifest_path, self.manifest)

    def write_transcript(self, result, output_formats, options):
        artifacts = self.directory / "artifacts"
        artifacts.mkdir()
        temporary = self.directory / "tmp"
        temporary.mkdir()
        for output_format in output_formats:
            name = f"transcript_{output_format}"
            filename = f"{name}.{output_format}"
            get_writer(output_format, str(temporary))(result, name, **options)
            (temporary / filename).replace(artifacts / filename)
            self.manifest["outputs"][name] = f"artifacts/{filename}"
        temporary.rmdir()

    def finish(self, status, diagnostic=None):
        self.manifest["status"] = status
        self.manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        if diagnostic is not None:
            stage = (
                "transcription"
                if self.manifest["formal_started"]
                else "automatic_precheck"
            )
            self.manifest["diagnostics"].append(
                {"stage": stage, "message": str(diagnostic)}
            )
        write_json(self.manifest_path, self.manifest)
