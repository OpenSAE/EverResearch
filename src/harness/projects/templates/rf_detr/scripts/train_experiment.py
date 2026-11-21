# ------------------------------------------------------------------------
# RF-DETR
# Copyright (c) 2025 Roboflow. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 [see LICENSE for details]
# ------------------------------------------------------------------------
"""Preview, launch, and inspect named RF-DETR training experiments from this checkout.

The launcher uses the installed RF-DETR training CLI and keeps each execution's metadata and artifacts under the
checkout's experiment directory. Use the existing training CLI directly for a caller-selected output directory.
"""

import argparse
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from time import monotonic
from typing import Any
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECORD_NAME = "manifest.json"
LEGACY_EXECUTION_RECORD = "execution.json"
COCO_SUBSET = "coco2017_subset"
EFFECTIVE_CONFIG = "metadata/effective_config.json"


def _experiment_name(value: str) -> str:
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", value) or value in {
        "run",
        "trial",
        "experiment",
        "default",
        "output",
        "test",
        "job",
        "untitled",
    }:
        raise argparse.ArgumentTypeError("Use one to three words describing the experiment, e.g. 'default_finetuning'.")
    return _canonical_purpose(value)


def _canonical_purpose(value: str) -> str:
    """Resolve the original fine-tuning label to the current experiment name."""
    return "pretrained_fine_tuning" if value == "pretrained_finetuning" else value


def _dataset_name(value: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("Use the dataset name with lowercase letters, digits and underscores.")
    return value


def _path_under_experiment(path: Path) -> Path:
    root = PROJECT_ROOT / "experiment"
    resolved = path.resolve()
    if not resolved.is_relative_to(root) or resolved == root:
        raise ValueError(f"Expected a path inside {root}.")
    return resolved


def _model_location(config_class: str) -> Path:
    prefix, _, name = config_class.rpartition(".")
    if prefix == "rfdetr.config" and name.startswith("RFDETR") and name.endswith("Config"):
        variant = name.removeprefix("RFDETR").removesuffix("Config")
        if variant.startswith("Seg"):
            return Path(f"rfdetr_segmentation_{variant.removeprefix('Seg').lower()}")
        if variant.startswith("Keypoint"):
            return Path(f"rfdetr_keypoint_{variant.removeprefix('Keypoint').lower()}")
        return Path(f"rfdetr_detection_{variant.lower()}")
    # Keep the qualified name for a caller's custom config class.
    if not re.fullmatch(r"(?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*", config_class, re.ASCII):
        raise ValueError(f"Invalid model config class: {config_class!r}.")
    name = re.sub(r"[^a-z0-9]+", "_", config_class.lower()).strip("_")
    return Path(f"custom_{name}")


def _training_plan(args: argparse.Namespace, fit_args: list[str]) -> tuple[Path, dict[str, Any], list[str]]:
    import yaml

    if any(arg.partition("=")[0] in {"--print_config", "--help", "-h"} for arg in fit_args):
        raise ValueError("Use --plan to preview the fit configuration or rfdetr fit --help for Lightning options.")

    command = [sys.executable, "-m", "rfdetr", "fit", "--config", str(args.config), *fit_args]
    preview = subprocess.run([*command, "--print_config"], capture_output=True, text=True, check=False)
    if preview.returncode:
        raise ValueError(preview.stderr.strip() or preview.stdout.strip())
    config = yaml.safe_load(preview.stdout)
    if not isinstance(config, dict) or "model" not in config:
        raise ValueError(
            "Expected the Lightning fit configuration. Use this command's fit --help for available options."
        )
    model = config["model"]
    model_class = model["model_config"]["class_path"]
    train_config = model["train_config"]["init_args"]
    if not train_config.get("dataset_dir"):
        raise ValueError("Set the input dataset directory in the fit configuration.")
    dataset = COCO_SUBSET if args.dataset == "coco2017_acceptance" else args.dataset
    directory = _path_under_experiment(
        PROJECT_ROOT / "experiment" / dataset / _model_location(model_class) / "train" / args.name
    )
    # The execution directory becomes the authoritative output for the trainer and the RF-DETR callbacks.
    train_config.pop("output_dir", None)
    config["trainer"].pop("default_root_dir", None)
    return directory, config, command


def _write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.tmp")
    temporary_path.write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    temporary_path.replace(path)


def _record_outputs(execution: Path) -> dict[str, str]:
    """Keep TensorBoard logs separate from user-facing metrics, weights and configurations."""
    artifacts = execution / "artifacts"
    events = sorted(item for item in artifacts.rglob("events.out.tfevents.*") if item.is_file())
    for item in events:
        destination = execution / "logs" / "tensorboard" / item.relative_to(artifacts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        item.rename(destination)
    hyperparameters = artifacts / "hparams.yaml"
    if hyperparameters.is_file():
        hyperparameters.rename(artifacts / "model_parameters.yaml")
    return {
        item.stem: item.relative_to(execution).as_posix() for item in sorted(artifacts.rglob("*")) if item.is_file()
    }


def _fit(args: argparse.Namespace, fit_args: list[str]) -> int:
    launched = monotonic()
    directory, config, command = _training_plan(args, fit_args)
    if getattr(args, "plan", False):
        print(json.dumps({"experiment_directory": str(directory), "fit_configuration": config}, indent=2, default=str))
        return 0

    from rfdetr.precheck import check_fit, checked_environment

    if args.action == "precheck":
        precheck = check_fit(command)
        print(json.dumps(precheck, indent=2))
        return precheck["returncode"]

    started = datetime.now(timezone.utc)
    run_id = f"{started:%Y%m%dT%H%M%S.%fZ}-{uuid4().hex}"
    execution = _path_under_experiment(directory / "executions" / run_id)
    artifacts = execution / "artifacts"
    artifacts.mkdir(parents=True)
    config["model"]["train_config"]["init_args"]["output_dir"] = str(artifacts)
    config["trainer"]["default_root_dir"] = str(artifacts)
    fit_command = [
        *command,
        f"--model.train_config.init_args.output_dir={artifacts}",
        f"--trainer.default_root_dir={artifacts}",
    ]
    record = {
        "status": "running",
        "started_at": started.isoformat(),
        "run_id": execution.name,
        "execution_id": execution.name,
        "subname": args.name,
        "dataset": args.dataset,
        "task": "train",
        "experiment": args.name,
        "working_directory": str(Path.cwd()),
        "model_config_class": config["model"]["model_config"]["class_path"],
        "command": fit_command,
        "environment": {
            "python": platform.python_version(),
            "rfdetr": version("rfdetr"),
            "torch": version("torch"),
            "lightning": version("pytorch-lightning"),
        },
        "fit_configuration": config,
        "effective_config": EFFECTIVE_CONFIG,
        "formal_started": False,
        "outputs": {},
    }
    _write_json(
        execution / EFFECTIVE_CONFIG,
        {
            **config,
            "component_paths": {
                "dataset": directory.relative_to(PROJECT_ROOT / "experiment").parts[0],
                "model": directory.parent.parent.name,
                "task": "train",
            },
        },
    )
    manifest = execution / RECORD_NAME
    _write_json(manifest, record)
    print(f"Execution directory: {execution}", flush=True)
    try:
        record["precheck"] = check_fit(command)
        if record["precheck"]["status"] == "failed":
            returncode = record["precheck"]["returncode"]
            record.update(status="failed", returncode=returncode)
            record["diagnostics"] = [{"stage": "automatic_precheck", "message": record["precheck"]["error"]}]
            print(f"Training precheck failed: {record['precheck']['error']}", file=sys.stderr)
            return returncode if returncode >= 0 else 128 - returncode
        record["precheck_seconds"] = monotonic() - launched
        record["formal_started"] = True
        _write_json(manifest, record)
        returncode = subprocess.run(fit_command, check=False, env=checked_environment()).returncode
        record.update(status="succeeded" if returncode == 0 else "failed", returncode=returncode)
        return returncode if returncode >= 0 else 128 - returncode
    except KeyboardInterrupt:
        record.update(status="interrupted", returncode=130)
        return 130
    except OSError as exc:
        record.update(status="failed", error=str(exc))
        raise
    finally:
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        record["outputs"] = _record_outputs(execution)
        if record["status"] == "succeeded" and not record["outputs"]:
            record["status"] = "stopped"
        if record.get("precheck", {}).get("samples_checked") is not None:
            report = execution / "reports/precheck.json"
            _write_json(report, record["precheck"])
            record["outputs"]["precheck"] = report.relative_to(execution).as_posix()
        _write_json(manifest, record)


def _read_execution(execution: Path) -> dict[str, Any] | None:
    """Read a current manifest or a frozen execution record, with its actual artifact directory."""
    for filename in (RECORD_NAME, f"metadata/{LEGACY_EXECUTION_RECORD}", LEGACY_EXECUTION_RECORD):
        path = _path_under_experiment(execution / filename)
        if path.is_file():
            artifacts = _path_under_experiment(execution / "artifacts")
            record = json.loads(path.read_text(encoding="utf-8"))
            if "outputs" in record:
                record["artifacts"] = sorted(
                    Path(path).relative_to("artifacts").as_posix()
                    for path in record["outputs"].values()
                    if Path(path).is_relative_to("artifacts")
                )
                if record["status"] == "succeeded":
                    record["status"] = "completed"
            return {**record, "directory": str(artifacts if artifacts.is_dir() else execution)}
    return None


def _resolve_legacy_results_path(path: Path) -> Path:
    """Resolve historical RF-DETR result addresses without changing the archived records."""
    parts = path.relative_to(PROJECT_ROOT / "experiment").parts
    if len(parts) >= 6 and parts[1] == "rfdetr":
        dataset, _, family, variant, task, purpose, *tail = parts
        families = {"detection": "detection", "segmentation": "segmentation", "keypoints": "keypoint"}
        if task != "train" or family not in families:
            return path
        model = f"rfdetr_{families[family]}_{variant}"
    elif len(parts) >= 2:
        dataset, model, *tail = parts
        if model.startswith("rfdetr_seg_"):
            model = f"rfdetr_segmentation_{model.removeprefix('rfdetr_seg_')}"
        elif model.startswith("rfdetr_") and not model.startswith(
            ("rfdetr_detection_", "rfdetr_segmentation_", "rfdetr_keypoint_")
        ):
            model = f"rfdetr_detection_{model.removeprefix('rfdetr_')}"
        if len(tail) < 2:
            return _path_under_experiment(PROJECT_ROOT / "experiment" / dataset / model / Path(*tail))
        task, purpose, *tail = tail
    else:
        return path
    dataset = COCO_SUBSET if dataset == "coco2017_acceptance" else dataset
    experiment = PROJECT_ROOT / "experiment" / dataset / model / task / _canonical_purpose(purpose)
    if len(tail) == 2 and tail[0] == "executions" and re.fullmatch(r"[0-9a-f]{32}", tail[1]):
        matches = list((experiment / "executions").glob(f"*-{tail[1]}"))
        if len(matches) == 1:
            return _path_under_experiment(matches[0])
    return _path_under_experiment(experiment.joinpath(*tail))


def _results(path: Path) -> int:
    directory = _path_under_experiment(path)
    if not directory.exists():
        directory = _resolve_legacy_results_path(directory)
    if directory.name == "artifacts":
        directory = directory.parent
    record = _read_execution(directory)
    results = [record] if record else []
    executions = directory / "executions"
    if not results and executions.is_dir():
        for item in sorted(executions.iterdir()):
            if item.is_dir() and (result := _read_execution(_path_under_experiment(item))) is not None:
                results.append(result)
    if not results:
        raise ValueError(f"No recorded executions under {directory}.")
    print(json.dumps(sorted(results, key=lambda record: record["started_at"]), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the experiment launcher and return its process status."""
    argv = sys.argv[1:] if argv is None else argv
    boundary = argv.index("--") if "--" in argv else len(argv)
    fit_args = argv[boundary + 1 :]
    parser = argparse.ArgumentParser(description="Preview, launch, and inspect named RF-DETR training experiments.")
    subparsers = parser.add_subparsers(dest="action", required=True)
    selection = argparse.ArgumentParser(add_help=False)
    selection.add_argument(
        "--dataset", required=True, type=_dataset_name, help="Actual dataset identity, e.g. coco or coco_subset."
    )
    selection.add_argument(
        "--name", required=True, type=_experiment_name, help="Research purpose, e.g. default_finetuning."
    )
    selection.add_argument(
        "--config", default="rfdetr_nano", help="Named Lightning recipe or path to a configuration file."
    )
    fit = subparsers.add_parser(
        "fit", parents=[selection], help="Run or preview training. Pass Lightning fit options after --."
    )
    fit.add_argument(
        "--plan", action="store_true", help="Print the resolved configuration and experiment path without writing."
    )
    subparsers.add_parser(
        "precheck", parents=[selection], help="Run the bounded training check without launching a named execution."
    )
    results = subparsers.add_parser("results", help="Read execution records from an experiment or execution directory.")
    results.add_argument("directory", type=Path)
    args = parser.parse_args(argv[:boundary])
    try:
        if args.action in {"fit", "precheck"}:
            return _fit(args, fit_args)
        if fit_args:
            parser.error("Only fit and precheck accept arguments after --.")
        return _results(args.directory)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{parser.prog}: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
