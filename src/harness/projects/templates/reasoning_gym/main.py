"""Dispatch Reasoning Gym task commands from the checkout.

Use this entry to run evaluation, training, and the evaluation dataset precheck.
"""

import argparse
from pathlib import Path
import runpy
import json
import sys

import yaml

ROOT = Path(__file__).resolve().parent
COMMANDS = {
    "evaluate": "tasks.evaluation.evaluate",
    "precheck": "tasks.evaluation.evaluate",
    "evaluate-local": "tasks.local_evaluation.evaluate_model",
    "train": "tasks.training.train_grpo",
    "train-single": "tasks.training.single_device",
    "generate-config": "tasks.evaluation.generate_config",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=[*COMMANDS, "read-run"])
    parser.add_argument("args", nargs=argparse.REMAINDER)
    command = parser.parse_args()
    args = command.args
    if command.command == "read-run":
        if len(args) != 1:
            parser.error("read-run expects a run directory")
        from reasoning_gym.run_records import read_run

        try:
            print(json.dumps(read_run(Path(args[0])), indent=2))
        except (OSError, ValueError) as error:
            parser.error(str(error))
        return
    if command.command in {"evaluate", "precheck"}:
        if not any(arg == "--config" or arg.startswith("--config=") for arg in args):
            defaults = yaml.safe_load((ROOT / "conf/config.yaml").read_text(encoding="utf-8"))
            args = ["--config", str(ROOT / defaults["evaluation"]["config"]), *args]
        if command.command == "precheck":
            args.append("--precheck")
    sys.argv = [f"{parser.prog} {command.command}", *args]
    runpy.run_module(COMMANDS[command.command], run_name="__main__")


if __name__ == "__main__":
    main()
