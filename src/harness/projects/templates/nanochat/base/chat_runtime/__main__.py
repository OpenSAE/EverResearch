"""EverResearch checks and managed runs for NanoChat."""

import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    precheck = commands.add_parser("precheck", help="Read real inputs and check a small model batch")
    precheck.add_argument("--config", type=Path, default=Path("conf/config.json"))
    precheck.add_argument("--task", choices=("tokenization", "base_training", "fine_tuning", "evaluation", "inference"))
    precheck.add_argument("--source", choices=("base", "sft", "rl"))
    precheck.add_argument("--rl", action="store_true", help="Check reinforcement-learning inputs")
    precheck.add_argument("--model-tag")
    precheck.add_argument("--step", type=int)
    precheck.add_argument("--device", default="cpu")
    launch = commands.add_parser("run", help="Precheck an existing workflow and record its execution")
    launch.add_argument("--config", type=Path, default=Path("conf/config.json"))
    launch.add_argument("--subname", required=True)
    launch.add_argument("workflow")
    launch.add_argument("task_args", nargs=argparse.REMAINDER, help="Arguments after the workflow name go to its original command")

    args = parser.parse_args()
    with args.config.open(encoding="utf-8") as stream:
        settings = json.load(stream)

    if args.command == "run":
        if args.workflow not in settings["workflows"]:
            launch.error("Choose a workflow from " + ", ".join(settings["workflows"]))
        args.task = settings["workflows"][args.workflow]["task"]
        args.rl = args.workflow == "reinforcement"
        task_args = args.task_args[1:] if args.task_args[:1] == ["--"] else args.task_args
        options = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        options.add_argument("--device-type")
        options.add_argument("--model-tag", "-g")
        options.add_argument("--model-step", "--step", "-s", type=int)
        options.add_argument("--source", "-i")
        if args.workflow == "base_train":
            options.add_argument("--resume-from-step", type=int, default=-1)
            options.add_argument("--depth", type=int, default=20)
            options.add_argument("--aspect-ratio", type=int, default=64)
            options.add_argument("--head-dim", type=int, default=128)
            options.add_argument("--max-seq-len", type=int, default=2048)
            options.add_argument("--window-pattern", default="SSSL")
        if args.workflow == "chat":
            options.add_argument("--prompt", "-p")
        selected, _ = options.parse_known_args(task_args)
        args.device = selected.device_type
        args.model_tag = selected.model_tag
        args.step = selected.model_step
        args.source = selected.source
        if args.workflow == "base_train":
            args.architecture = selected
            if selected.resume_from_step >= 0:
                args.source = "base"
                args.step = selected.resume_from_step
                args.model_tag = selected.model_tag or f"d{selected.depth}"
        if args.workflow == "chat_eval" and args.source not in {"sft", "rl"}:
            launch.error("chat_eval requires --source sft or --source rl")
        if args.workflow == "chat":
            if selected.prompt in {None, "", "clear"}:
                launch.error("Managed chat requires --prompt. Run python -m scripts.chat_cli for interactive chat.")
            args.source = args.source or "sft"
            args.prompt = selected.prompt

        from nanochat.common import autodetect_device_type
        from nanochat.managed_run import run

        args.device = args.device or autodetect_device_type()
        return run(args, settings, task_args)

    args.task = args.task or settings["task"]
    if args.task not in settings["catalogs"]["task"]:
        precheck.error(f"Unknown task in the project configuration: {args.task}")
    if args.task == "base_training" and args.source is None and (args.model_tag is not None or args.step is not None):
        args.source = "base"
    if args.rl and args.task != "fine_tuning":
        precheck.error("--rl requires --task fine_tuning")

    from tasks.precheck.task import check

    print(json.dumps(check(args), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
