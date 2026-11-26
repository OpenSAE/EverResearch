"""Installed commands for checking and running AgentFlow workflows."""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog="agentflow")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("precheck", help="Check benchmark data and a selected engine")
    check.add_argument("--data-file", required=True)
    check.add_argument("--index", type=int, default=0)
    check.add_argument("--model")
    check.add_argument("--base-url")
    check.add_argument("--probe-model", action="store_true")

    commands.add_parser("infer", help="Run the AgentFlow inference example", add_help=False)
    commands.add_parser("benchmark", help="Run the benchmark solver", add_help=False)
    commands.add_parser("score", help="Score saved benchmark results", add_help=False)
    commands.add_parser("train", help="Show or run the Flow-GRPO training command", add_help=False)

    args, remaining = parser.parse_known_args()
    if args.command == "precheck":
        if remaining:
            check.error(f"unrecognized arguments: {' '.join(remaining)}")
        if args.probe_model and not args.model:
            check.error("--probe-model requires --model")
        from dotenv import load_dotenv

        from agentflow.precheck.gate import precheck

        load_dotenv(Path.cwd() / ".env")

        try:
            summary = precheck(
                args.data_file, args.index, args.model,
                base_url=args.base_url, probe_model=args.probe_model,
            )
        except (OSError, ValueError, ImportError) as exc:
            check.error(str(exc))
        print(json.dumps(summary))
        return

    from dotenv import load_dotenv

    load_dotenv(Path.cwd() / ".env")
    sys.argv = [f"agentflow {args.command}", *remaining]
    if args.command == "infer":
        from agentflow.solver import main as infer, parse_arguments

        infer(parse_arguments())
    elif args.command == "benchmark":
        from agentflow.benchmarks.solve import main as benchmark, parse_arguments

        benchmark(parse_arguments())
    elif args.command == "score":
        from agentflow.benchmarks.calculate_score_unified import main as score

        score()
    else:
        from agentflow.training.train_agent import main as train

        train()
