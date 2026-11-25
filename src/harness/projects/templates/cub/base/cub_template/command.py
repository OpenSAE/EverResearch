"""Purpose: Provision of precheck of classifications, comparison with workload performance, training and access to operational lists.

Scope of application: normal command entry for reference items.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="operation", required=True)
    for name in ("run", "precheck", "benchmark", "train"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, help="Default From Item conf/config.yaml Read")
        command.add_argument("--subname", required=True, help="One to three terms describing experimental use")
        command.add_argument("--data-root", type=Path)
        command.add_argument("--set", action="append", default=[], metavar="GROUP=VALUE")
        if name == "benchmark":
            command.add_argument(
                "--candidate-workers", type=int, help="Candidates for comparison with the current number of work processes"
            )
    inspect = commands.add_parser("inspect")
    inspect.add_argument("run_dir", type=Path)
    return result


def main(argv=None):
    started = perf_counter()
    commands = parser()
    args = commands.parse_args(argv)
    if args.operation == "inspect":
        try:
            path = args.run_dir / "metadata/manifest.json"
            print(json.dumps(json.loads(path.read_text()), ensure_ascii=False, indent=2))
            return 0
        except (OSError, ValueError) as exc:
            print(f"Failed to read list:{exc}", file=sys.stderr)
            return 1
    from .runtime.records import experiment_root, normalize_subname

    try:
        subname = normalize_subname(args.subname)
        config_path = args.config or experiment_root().parent / "conf/config.yaml"
    except ValueError as exc:
        commands.error(str(exc))
    from .runtime.runner import execute

    return execute(
        args.operation,
        config_path,
        subname,
        data_root=args.data_root,
        candidate_workers=getattr(args, "candidate_workers", None),
        overrides=args.set,
        started=started,
    )
