"""Keep effective workflow settings and outputs together in a named run.

Evaluation and single-device training use the checkout layout. Legacy readers can still
open the original flat result directories.
"""

from datetime import datetime, timezone
from functools import lru_cache
import json
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile
from uuid import uuid4

import yaml


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".pending_", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, indent=2)
            stream.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


# Keep the project writer aligned with EverResearch's study-name rules.
_ENGINEERING_WORDS = frozenset({
    "dataset", "datasets", "filename", "filenames", "metadata", "postprocessing",
    "precheck", "preprocessing", "runtime", "runtimes", "tokenization", "tokenizer",
    "tokenizers", "wildcard", "wildcards", "workflow", "workflows",
})
_INITIALISMS = frozenset({"ai", "id", "io", "os"})


@lru_cache(maxsize=1)
def english_dictionary():
    from spellchecker import SpellChecker

    return SpellChecker(language="en").word_frequency.dictionary


def validate_study(study):
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", study) or study in {
        "run", "trial", "experiment", "default", "output", "test", "job", "untitled",
        "artifacts", "logs", "metadata", "reports", "tmp", "executions",
    }:
        raise ValueError("Use one to three descriptive words separated by underscores for --study.")
    if not any(
        len(word) >= 2 and word not in _INITIALISMS
        and (word in _ENGINEERING_WORDS or word in english_dictionary())
        for word in study.split("_")
    ):
        raise ValueError("Include at least one complete English word in --study.")


class EvaluationRecord:
    def __init__(self, root, model, task, study, configuration, base_url=None, resume=None):
        validate_study(study)
        self.directory = Path(root) / "experiment" / "procedural" / model / task / study
        paths = {"dataset": "procedural", "model": model, "task": task}
        self.configuration = {"component_paths": paths, "evaluation": configuration}
        if base_url is not None:
            self.configuration["base_url"] = base_url
        self.manifest_path = self.directory / "metadata" / "manifest.json"
        config_path = self.directory / "config.yaml"
        if resume is None:
            self.directory.mkdir(parents=True, exist_ok=False)
            self.manifest = {
                "schema_version": 1, "project_id": "reasoning_gym", "run_id": str(uuid4()),
                "task": task, "subname": study, "effective_config": "config.yaml",
                "configuration": self.configuration, "formal_started": False, "outputs": {},
                "status": "running", "diagnostics": [], "environment": {"python": sys.executable},
            }
            config_path.write_text(yaml.safe_dump(self.configuration, sort_keys=False), encoding="utf-8")
        else:
            if Path(resume).resolve() != self.directory.resolve():
                raise ValueError("The managed resume directory must match the saved study.")
            self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if self.configuration != yaml.safe_load(config_path.read_text(encoding="utf-8")):
                raise ValueError("Resume settings differ from the saved effective configuration.")
            self.manifest.update(status="running", diagnostics=[], formal_started=False)
        self.save()

    def save(self):
        self.manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        for group in ("reports", "artifacts"):
            for path in (self.directory / group).glob("*.json"):
                self.manifest["outputs"][path.stem] = f"{group}/{path.name}"
        write_json(self.manifest_path, self.manifest)

    def start(self, report, elapsed):
        write_json(self.directory / "reports" / "precheck.json", report)
        self.manifest.update(formal_started=True, precheck_seconds=elapsed)
        self.save()

    def finish(self, status, error=None):
        self.manifest["status"] = status
        if error is not None:
            stage = "formal_execution" if self.manifest["formal_started"] else "automatic_precheck"
            self.manifest["diagnostics"].append({"stage": stage, "message": str(error) or status})
        self.save()


def read_run(directory):
    """Read a managed study or a legacy flat evaluation directory."""
    if not directory.is_dir():
        raise ValueError(f"Run directory does not exist: {directory}")
    files = {
        "manifest": ("metadata/manifest.json", "manifest.json"),
        "summary": ("reports/summary.json", "summary.json"),
        "results": ("artifacts/results.json", "results.json"),
        "timing": ("reports/timing.json",),
    }
    result = {}
    for name, candidates in files.items():
        candidate = next((directory / path for path in candidates if (directory / path).is_file()), None)
        if candidate is not None:
            result[name] = json.loads(candidate.read_text(encoding="utf-8"))
    if not result:
        raise ValueError(f"No evaluation records found in {directory}")
    return result
