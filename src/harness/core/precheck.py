"""Check for automatic pre-checking and blocking evidence from the official mission entrance.

Read only one successful and one failed precheck check for a central command.
The central experimental rules are used for the attribution of the products and the actual reading of the calculations and the results are the responsibility of the project entrance..
"""

import math
from pathlib import Path

import yaml

from .experiment import MANIFESTS, check_run, read_record
from .layout import experiment_rules


def check_precheck(root, succeeded, rejected, *, max_seconds, max_samples):
    """Check saved evidence from two invocations of the formal task entry."""
    root = Path(root).resolve(strict=True)
    if not math.isfinite(max_seconds) or max_seconds <= 0:
        raise ValueError("Pre-check time limit must be limited positive.")
    if type(max_samples) is not int or max_samples <= 0:
        raise ValueError("The maximum number of pre-screened samples processed must be a positive integer")
    rules = experiment_rules(root)
    violations = []

    def fail(path, rule, expected):
        violations.append({"path": str(path), "rule": rule, "expected": expected})

    def load_run(value):
        directory = (root / value).resolve(strict=True)
        if not directory.is_dir() or not directory.is_relative_to(root / "experiment"):
            raise ValueError(f"Provision of projects experiment/ _Other Organiser:{value}")
        relative = directory.relative_to(root)
        count = len(violations)
        check_run(directory, relative, rules, fail)
        if len(violations) == count:
            manifest = next(directory / name for name in MANIFESTS if (directory / name).is_file())
            return relative, read_record(manifest)
        return relative, None

    passed_path, passed = load_run(succeeded)
    failed_path, failed = load_run(rejected)
    if passed_path == failed_path:
        raise ValueError("Provides two implementation directories of successful and precheck failures, respectively")
    if passed is not None:
        if passed["status"] != "succeeded" or passed.get("formal_started") is not True:
            fail(passed_path, "formal_execution", "Successful samples were entered and formally calculated")
        elapsed = passed.get("precheck_seconds")
        if (type(elapsed) not in {int, float} or not math.isfinite(elapsed)
                or not 0 <= elapsed <= max_seconds):
            fail(passed_path, "precheck_duration", f"The entrance to precheck is running out of time. {max_seconds:g} seconds")
        report_path = passed["outputs"].get("precheck")
        samples = None
        if report_path:
            try:
                samples = read_record(root / passed_path / report_path).get("samples_checked")
            except (OSError, ValueError, yaml.YAMLError):
                pass
        if type(samples) is not int or not 1 <= samples <= max_samples:
            fail(
                passed_path, "precheck_samples",
                f"The precheck report records the number of actual samples processed in the range of 1 to {max_samples}",
            )
    if failed is not None:
        diagnostics = failed.get("diagnostics", [])
        if not isinstance(diagnostics, list) or not any(
            isinstance(item, dict) and item.get("stage") == "automatic_precheck"
            and isinstance(item.get("message"), str) and item["message"].strip()
            for item in diagnostics
        ):
            fail(failed_path, "precheck_error", "Record the actual reasons for the failure of automatic precheck")
        if failed["status"] != "failed" or failed.get("formal_started") is not False:
            fail(failed_path, "precheck_blocking", "precheck failed and the official calculation has not yet started")
    return {"project": str(root), "passed": not violations, "violations": violations}
