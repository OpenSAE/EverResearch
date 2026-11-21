"""Configure managed and standalone LLMLingua-2 compression runs."""

import argparse
import json
import re
from time import perf_counter
from datetime import datetime, timezone
from itertools import islice
from pathlib import Path

from ..datasets.prompts import read_prompt_samples
from ..tasks.compression import compress_samples
from ..tasks.precheck import preview_compression
from .config import load_defaults
from .records import (
    component_paths,
    experiment_root,
    initialize_run,
    manifest_path,
    read_run,
    run_directory,
    write_json,
)

def add_compression_arguments(parser):
    parser.add_argument(
        "--model_name", default=load_defaults()["default_batch_model"], help="Model ID or path"
    )
    parser.add_argument("--model_revision", help="Hugging Face model revision")
    parser.add_argument(
        "--load_origin_from", required=True, type=Path, help="Input JSON"
    )
    parser.add_argument("--load_key", default="prompt", help="Input text field")
    parser.add_argument("--save_key", default="compressed_prompt", help="Output field")
    parser.add_argument("--device_map", default="cuda", help="Transformers device map")
    parser.add_argument("--compression_rate", type=float, default=0.5)
    parser.add_argument("--target_token", type=int, default=-1)
    parser.add_argument("--target_context", type=int, default=-1)
    parser.add_argument("--context_level_compression_rate", type=float, default=1.0)
    parser.add_argument("--context_level_target_token", type=int, default=-1)
    parser.add_argument(
        "--force_tokens", help=r"Comma-separated tokens to keep. Use \n for newline."
    )
    for name, default in (
        ("use_token_level_filter", True),
        ("use_context_level_filter", False),
        ("drop_consecutive", True),
        ("force_reserve_digit", False),
    ):
        # BooleanOptionalAction was added after LLMLingua's Python 3.8 minimum.
        parser.add_argument(f"--{name}", dest=name, action="store_true")
        parser.add_argument(f"--no-{name}", dest=name, action="store_false")
        parser.set_defaults(**{name: default})


def compression_options(args):
    force_tokens = (
        [token.replace(r"\n", "\n") for token in args.force_tokens.split(",")]
        if args.force_tokens is not None
        else []
    )
    return {
        "rate": args.compression_rate,
        "target_token": args.target_token,
        "use_context_level_filter": args.use_context_level_filter,
        "use_token_level_filter": args.use_token_level_filter,
        "target_context": args.target_context,
        "context_level_rate": args.context_level_compression_rate,
        "context_level_target_token": args.context_level_target_token,
        "force_tokens": force_tokens,
        "drop_consecutive": args.drop_consecutive,
        "force_reserve_digit": args.force_reserve_digit,
    }


def build_compressor(config):
    from .. import PromptCompressor

    revision = config.get("model_revision")
    return PromptCompressor(
        model_name=config["model_name"],
        device_map=config["device_map"],
        model_config={"revision": revision} if revision else {},
        use_llmlingua2=True,
    )


def run_batch(config):
    started = perf_counter()
    samples = read_prompt_samples(Path(config["input"]), config["input_key"])
    if config.get("precheck_only") and not samples:
        raise ValueError("Precheck needs at least one sample with text.")
    if config["limit"] is not None:
        samples = dict(islice(samples.items(), config["limit"]))
    run = run_directory(config, Path(config["experiment_root"]))
    manifest = initialize_run(run, config)
    manifest["formal_started"] = False
    try:
        if samples:
            compressor = build_compressor(config)
            first, checked = preview_compression(
                compress_samples(
                    compressor, samples, config["input_key"],
                    config["output_key"], config["compression"],
                )
            )
            precheck = "reports/precheck.json"
            write_json(run / precheck, {"sample_id": first[0], "samples_checked": 1})
            manifest["precheck_seconds"] = perf_counter() - started
            manifest["outputs"]["precheck"] = precheck
            manifest["formal_started"] = not config.get("precheck_only")
            results = dict(checked)
        else:
            results = {}
        write_json(run / manifest["artifact"], results)
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update(status="failed", error=str(exc))
        if samples and "precheck_seconds" not in manifest:
            manifest["diagnostics"] = [{"stage": "automatic_precheck", "message": str(exc)}]
        raise
    else:
        manifest.update(
            status="succeeded",
            sample_count=len(results),
        )
        manifest["outputs"]["compressed_prompts"] = manifest["artifact"]
    finally:
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        write_json(manifest_path(run), manifest)
    return run


def label(value, max_words):
    return bool(
        re.fullmatch(rf"[a-z]+(?:_[a-z]+){{0,{max_words - 1}}}", value)
        and value not in {
            "run", "trial", "experiment", "default", "output", "test",
            "job", "untitled", "results",
        }
    )


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m llmlingua")
    commands = parser.add_subparsers(required=True, dest="command")
    batch = commands.add_parser("compress", help="Compress a JSON benchmark input")
    add_compression_arguments(batch)
    batch.add_argument(
        "--dataset", required=True, help="Dataset identity in result paths"
    )
    batch.add_argument("--name", help="Experiment purpose")
    batch.add_argument("--limit", type=int, help="Process the first N eligible samples")
    batch.add_argument("--experiment-root", type=Path, default=experiment_root())
    mode = batch.add_mutually_exclusive_group()
    mode.add_argument("--show-config", action="store_true", help="Print effective settings")
    mode.add_argument("--precheck", action="store_true", help="Validate a single sample")
    show = commands.add_parser(
        "show", help="Read a run's manifest, config and predictions"
    )
    show.add_argument("run", type=Path)
    args = parser.parse_args(argv)
    if args.command == "show":
        try:
            print(json.dumps(read_run(args.run), indent=4, ensure_ascii=False))
        except (OSError, ValueError, KeyError) as exc:
            show.error(str(exc))
        return

    if not re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", args.dataset):
        batch.error(
            "--dataset must be a lowercase identifier like meetingbank or gsm8k"
        )
    purpose = args.name
    if purpose is None:
        purpose = "compression_precheck" if args.precheck else "prompt_compression"
    if not label(purpose, 3):
        batch.error("--name must describe the purpose in one to three lowercase words")
    if args.limit is not None and args.limit < 1:
        batch.error("--limit must be positive")
    if args.experiment_root is None and not args.show_config:
        batch.error("Use --experiment-root to choose a result directory outside an LLMLingua checkout.")
    options = compression_options(args)
    if not 0 <= options["rate"] <= 1 or not 0 <= options["context_level_rate"] <= 1:
        batch.error("Compression rates must be between 0 and 1")
    config = {
        "dataset": args.dataset,
        "name": purpose,
        "model_name": args.model_name,
        "model_revision": args.model_revision,
        "device_map": args.device_map,
        "input": str(args.load_origin_from.resolve()),
        "input_key": args.load_key,
        "output_key": args.save_key,
        "limit": 1 if args.precheck else args.limit,
        "precheck_only": args.precheck,
        "experiment_root": str(args.experiment_root.resolve()) if args.experiment_root else None,
        "compression": options,
    }
    config["component_paths"] = component_paths(config)
    if args.show_config:
        print(json.dumps(config, indent=4, ensure_ascii=False))
        return
    try:
        print(run_batch(config))
    except (OSError, ValueError) as exc:
        batch.error(str(exc))


def legacy_main(argv=None):
    parser = argparse.ArgumentParser(description="Compress benchmark prompts.")
    add_compression_arguments(parser)
    parser.add_argument("--compressor", default="llmcomp", help=argparse.SUPPRESS)
    parser.add_argument("--save_path", required=True, type=Path)
    args = parser.parse_args(argv)

    samples = read_prompt_samples(args.load_origin_from, args.load_key)
    results = {}
    if args.save_path.exists():
        with args.save_path.open(encoding="utf-8") as stream:
            results = json.load(stream)
    pending = {
        index: sample for index, sample in samples.items() if index not in results
    }
    if pending:
        compressor = build_compressor(vars(args))
        _, checked = preview_compression(
            compress_samples(
                compressor, pending, args.load_key, args.save_key, compression_options(args)
            )
        )
        for index, result in checked:
            results[index] = result
            write_json(args.save_path, results)
    else:
        write_json(args.save_path, results)
    print(args.save_path)
