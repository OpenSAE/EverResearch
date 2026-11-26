"""Run an existing NanoChat command with a recorded EverResearch precheck."""

from datetime import datetime, timezone
from itertools import count
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from uuid import uuid4

from tasks.precheck.task import check


def write_record(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run(args, settings, task_args):
    dataset = settings["dataset"]
    if args.task == "fine_tuning" or (args.task == "evaluation" and args.source in {"sft", "rl"}):
        dataset = "conversations"
    elif args.task == "inference":
        dataset = "tokenization"
    configuration = {
        "dataset": dataset,
        "model": None if args.task == "tokenization" else settings["model"],
        "task": args.task,
        "workflow": args.workflow,
        "precheck": {
            "device": args.device, "source": args.source, "model_tag": args.model_tag,
            "step": args.step,
        },
        "arguments": task_args,
        "resources": {name: os.environ[name] for name in (
            "NANOCHAT_BASE_DIR", "NANOCHAT_CLIMBMIX_DIR", "NANOCHAT_TASK_DATA_DIR",
        ) if name in os.environ},
        "python": sys.executable,
    }
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", args.subname) or args.subname in {
        "default", "experiment", "job", "output", "run", "test", "trial", "untitled",
    }:
        raise ValueError("--subname must contain one to three lowercase words separated by underscores")
    root = args.config.resolve().parent.parent / "experiment"
    location = root.joinpath(*(configuration[key] for key in ("dataset", "model", "task")
                               if configuration[key] is not None), args.subname, "executions")
    for attempt in count(1):
        name = "attempt_" + "_".join("zero one two three four five six seven eight nine".split()[int(n)]
                                     for n in str(attempt))
        directory = location / name
        try:
            directory.mkdir(parents=True)
            break
        except FileExistsError:
            continue

    (directory / "metadata").mkdir()
    (directory / "reports").mkdir()
    manifest = {
        "run_id": uuid4().hex, "subname": args.subname, "execution_name": name,
        "task": args.task, "status": "running", "effective_config": "config.json",
        "created_at": datetime.now(timezone.utc).isoformat(), "formal_started": False,
        "outputs": {}, "diagnostics": [],
    }
    manifest_path = directory / "metadata/manifest.json"
    write_record(directory / "config.json", configuration)
    write_record(manifest_path, manifest)
    print(directory, flush=True)

    started = time.monotonic()
    try:
        report = check(args)
    except Exception as error:
        manifest["status"] = "failed"
        manifest["diagnostics"].append({"stage": "automatic_precheck", "message": str(error)})
        write_record(manifest_path, manifest)
        print(f"Precheck failed: {error}", file=sys.stderr)
        return 1

    manifest["precheck_seconds"] = time.monotonic() - started
    write_record(directory / "reports/precheck.json", report)
    manifest["outputs"]["precheck"] = "reports/precheck.json"
    if args.device.startswith("cuda"):
        import torch

        torch.cuda.empty_cache()
    command = [sys.executable, "-m", settings["workflows"][args.workflow]["module"], *task_args]
    with (directory / "reports/console.txt").open("w", encoding="utf-8") as output:
        manifest["formal_started"] = True
        write_record(manifest_path, manifest)
        try:
            returncode = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, check=False).returncode
        except KeyboardInterrupt:
            returncode = 130
        except OSError as error:
            manifest["diagnostics"].append({"stage": "launch", "message": str(error)})
            returncode = 1

    manifest["outputs"]["console"] = "reports/console.txt"
    manifest["status"] = "succeeded" if returncode == 0 else "interrupted" if returncode == 130 else "failed"
    manifest["returncode"] = returncode
    write_record(manifest_path, manifest)
    return returncode
