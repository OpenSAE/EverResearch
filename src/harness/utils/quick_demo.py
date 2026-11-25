"""Run a small onboarding and reproduction demo in a new workspace.

The demo uses synthetic inputs and standard-library project commands. It leaves
a before-and-after pair of example directories for inspection.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from harness.core.experiment import check_experiment
from harness.core.project import check_project
from harness.projects.onboarding import format_preview, preview


RUNNER = """from pathlib import Path
import json
import sys
from uuid import uuid4

from datasets.synthetic.samples import load
from models.baseline.predictor import predict
from tasks.evaluation.metric import score
from tasks.precheck.gate import validate


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\\n", encoding="utf-8")


def run(configuration, execution):
    config = json.loads(Path(configuration).read_text(encoding="utf-8"))
    values = load()
    validate(values)
    metric = score(values, predict(values, config["offset"]))
    root = Path("experiment") / config["dataset"] / config["model"] / config["task"] / "measure_error" / execution
    (root / "reports").mkdir(parents=True)
    write(root / "config.json", config)
    write(root / "reports/metrics.json", {"mean_squared_error": metric})
    write(root / "manifest.json", {
        "run_id": str(uuid4()),
        "subname": "measure_error",
        "execution_name": execution,
        "effective_config": "config.json",
        "status": "succeeded",
        "outputs": {"metrics": "reports/metrics.json"},
    })
    print(root)


if __name__ == "__main__":
    run(*sys.argv[1:])
"""

FILES = {
    "base/run.py": RUNNER,
    "datasets/synthetic/samples.py": "def load():\n    return [1, 3, 5, 7]\n",
    "models/baseline/predictor.py": "def predict(values, offset):\n    return sum(values) / len(values) + offset\n",
    "tasks/evaluation/metric.py": "def score(values, prediction):\n    return sum((value - prediction)**2 for value in values) / len(values)\n",
    "tasks/precheck/gate.py": "def validate(values):\n    if not values:\n        raise ValueError('Expected at least one observation')\n    return len(values)\n",
    "doc/README.md": "# SignalStudy documentation\n\n[Environment](environment/README.md)\n",
    "doc/environment/README.md": "# Environment\n\nRun with Python on your laptop.\n",
    "README.md": "# SignalStudy\n\nRun python -BS -m base.run conf/config.json baseline.\n",
    "conf/config.json": json.dumps({"dataset": "synthetic", "model": "baseline",
                                   "task": "evaluation", "offset": 0})+"\n",
}

BEFORE = {
    "train.py": "# Example training entry\n",
    "eval.py": "# Example evaluation entry\n",
    "train_v2_final.py": "# Example variant to inspect\n",
    "configs/baseline.json": FILES["conf/config.json"],
    "outputs/run_0412/metrics.json": '{"mean_squared_error": 5.0}\n',
}


def write_tree(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_experiment(root, configuration, name):
    command = [sys.executable, "-BS", "-m", "base.run", str(configuration), name]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=True)
    return root / result.stdout.strip()


def main(argv):
    parser = argparse.ArgumentParser(prog="rh utils quick-demo", description=__doc__)
    parser.add_argument("workspace", type=Path, help="New directory for the demo")
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    try:
        workspace.mkdir()
        before, project = workspace / "MixedStudy", workspace / "SignalStudy"
        write_tree(before, BEFORE)
        print(format_preview(preview(before)))
        print("\nThe organized example is ready in SignalStudy.")
        write_tree(project, FILES)
        original = run_experiment(project, "conf/config.json", "baseline")
        repeat = run_experiment(project, original / "config.json", "reproduction")
        first = (original / "reports/metrics.json").read_bytes()
        second = (repeat / "reports/metrics.json").read_bytes()
        if first != second or not check_project(project)["passed"] or not check_experiment(project)["passed"]:
            raise ValueError("The demo's structure, run records, or recorded metrics did not match")
        print("Project structure and both experiment records passed verification.")
        print(f"Baseline and reproduction match: {json.loads(first)}")
        print(f"Inspect both examples in {workspace}")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
