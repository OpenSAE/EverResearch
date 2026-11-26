"""Check one sample through the selected task and round-trip its result."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter


def check_sample(probe):
    started = perf_counter()
    result = probe()
    with TemporaryDirectory(prefix="mathvista-precheck-") as directory:
        report = Path(directory) / "sample.json"
        report.write_text(json.dumps(result), encoding="utf-8")
        json.loads(report.read_text(encoding="utf-8"))
    return {"samples_checked": 1, "seconds": perf_counter() - started, "sample": result}
