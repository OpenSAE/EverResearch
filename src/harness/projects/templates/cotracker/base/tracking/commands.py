"""Dispatch CoTracker commands and preserve options for the original research workflows."""

import argparse
import json
import os
from pathlib import Path
import re
import sys


UPSTREAM_COMMANDS = {
    "offline-demo": "cotracker.tracking.offline_demo",
    "online-demo": "cotracker.tracking.online_demo",
    "evaluate": "cotracker.evaluation.evaluate",
    "train-kubric": "cotracker.training.train_kubric",
    "train-real-video": "cotracker.training.real_video",
}


def study_name(value):
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", value) or value in {
        "run", "trial", "experiment", "default", "output", "test", "job", "untitled",
    }:
        raise argparse.ArgumentTypeError("Use one to three lowercase words separated by underscores")
    return value


def main(argv=None, default_workspace=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] in UPSTREAM_COMMANDS:
        module_name = UPSTREAM_COMMANDS[arguments[0]]
        os.execv(sys.executable, [sys.executable, "-m", module_name, *arguments[1:]])

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in UPSTREAM_COMMANDS:
        subparsers.add_parser(action, help="Run the corresponding upstream workflow")
    for action in ("track", "precheck"):
        command = subparsers.add_parser(action, help="Track points or verify tracking inputs and model")
        command.add_argument("--workspace", type=Path, default=default_workspace or Path.cwd())
        command.add_argument("--video")
        command.add_argument("--checkpoint")
        command.add_argument("--grid-size", type=int)
        command.add_argument("--grid-query-frame", type=int)
        command.add_argument("--backward-tracking", action=argparse.BooleanOptionalAction)
        command.add_argument("--device")
        command.add_argument("--subname", type=study_name)
        command.add_argument("--print-config", action="store_true")
    inspect = subparsers.add_parser("inspect", help="Read a tracking result and check its declared files")
    inspect.add_argument("directory", type=Path)
    args = parser.parse_args(arguments)
    try:
        if args.action == "inspect":
            from cotracker.records import read_tracking_run

            result = read_tracking_run(args.directory)
        else:
            from cotracker.workflow import run_tracking

            result = run_tracking(args, precheck_only=args.action == "precheck")
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f"CoTracker: {error}\n")
    print(json.dumps(result, indent=2))
    return 0
