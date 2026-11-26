"""Create and read run records for managed depth workflows."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
import re


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _alphabetic_index(index):
    name = ""
    while index >= 0:
        index, remainder = divmod(index, 26)
        name = chr(ord("a") + remainder) + name
        index -= 1
    return name


class RunRecord:
    def __init__(self, args, config, files):
        self.outputs = {}
        self.manifest = None
        if args.outdir:
            self.directory = args.outdir
            self.directory.mkdir(parents=True, exist_ok=True)
            return
        if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", args.study) or args.study in {
            "default", "experiment", "job", "output", "run", "test", "trial", "untitled",
        }:
            raise ValueError("Use one to three descriptive lowercase words for --study, joined by underscores.")
        self.directory = (
            args.workspace / "experiment" / config["dataset"] / config["model"] / config["task"] / args.study
        )
        self.directory.mkdir(parents=True, exist_ok=False)
        (self.directory / "artifacts").mkdir()
        (self.directory / "metadata").mkdir()
        write_json(self.directory / "config.json", config)
        self.manifest = {
            "run_id": str(uuid4()),
            "subname": args.study,
            "task": config["task"],
            "status": "running",
            "formal_started": False,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "effective_config": "config.json",
            "outputs": {},
            "sources": [str(file.resolve()) for file in files],
        }
        self._save()

    def _save(self):
        write_json(self.directory / "metadata" / "manifest.json", self.manifest)

    def output_path(self, source, index, purpose, suffix):
        if self.manifest is None:
            extra = "_raw_depth_meter" if purpose == "raw_depth_meter" else ""
            return self.directory / f"{source.stem}{extra}{suffix}"
        name = f"{purpose}_{_alphabetic_index(index)}"
        return self.artifact(name, suffix)

    def artifact(self, name, suffix):
        path = Path("artifacts") / f"{name}{suffix}"
        self.outputs[name] = path.as_posix()
        return self.directory / path

    def start_work(self, report):
        if self.manifest is not None:
            path = Path("reports/precheck.json")
            (self.directory / path.parent).mkdir()
            write_json(self.directory / path, report)
            self.outputs["precheck"] = path.as_posix()
            self.manifest["precheck_seconds"] = report["elapsed_seconds"]
            self.manifest["formal_started"] = True
            self.manifest["outputs"] = self.outputs.copy()
            self._save()

    def finish(self, status, error=None):
        if self.manifest is not None:
            self.manifest["status"] = status
            self.manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
            self.manifest["outputs"] = {
                name: path for name, path in self.outputs.items() if (self.directory / path).is_file()
            }
            if error is not None:
                self.manifest["error"] = str(error)
                if not self.manifest["formal_started"]:
                    self.manifest["diagnostics"] = [
                        {"stage": "automatic_precheck", "message": str(error)}
                    ]
            self._save()


def effective_options(args):
    return {key: str(value.resolve()) if isinstance(value, Path) else value for key, value in vars(args).items()}


def read_run(path):
    manifest = json.loads((path / "metadata" / "manifest.json").read_text())
    manifest["configuration"] = json.loads((path / manifest["effective_config"]).read_text())
    return manifest
