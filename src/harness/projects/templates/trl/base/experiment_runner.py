"""Connect the maintained TRL recipe to its data, model and supervised trainer.

This launcher records a fresh experiment and runs the trainer's bounded gate
before the optional formal operation.
"""

import argparse
import json
import re
import shutil
import tomllib
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from trl import DatasetMixtureConfig, ModelConfig, ScriptArguments, SFTConfig
from trl.precheck import check_supervised_batch
from trl.scripts.sft import create_trainer, train_and_save


ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    temporary = path.with_name(f".{path.name}.writing")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run(config, directory, *, precheck_only):
    for category in ("artifacts", "metadata", "reports", "tmp"):
        (directory / category).mkdir()
    config["training"]["output_dir"] = str(directory / "tmp/checkpoint")
    write_json(directory / "metadata/config.json", config)

    manifest = {
        "run_id": str(uuid4()), "subname": directory.name, "task": config["task"]["name"],
        "effective_config": "metadata/config.json", "status": "running", "outputs": {},
        "formal_started": False, "diagnostics": [],
    }
    manifest_path = directory / "metadata/manifest.json"
    write_json(manifest_path, manifest)
    started = perf_counter()
    try:
        dataset = config["dataset"]
        arguments = SFTConfig(**config["training"])
        script_args = ScriptArguments(dataset_name=dataset["repository"], dataset_config=dataset["configuration"],
                                      dataset_train_split=dataset["split"])
        model = ModelConfig(model_name_or_path=config["model"]["repository"],
                            model_revision=config["model"]["revision"])
        trainer = create_trainer(script_args, arguments, model, DatasetMixtureConfig())
        config["resolved_training"] = arguments.to_dict()
        write_json(directory / "metadata/config.json", config)
        report = check_supervised_batch(trainer)
        manifest["precheck_seconds"] = perf_counter() - started
        write_json(directory / "reports/precheck.json", report)
        manifest["outputs"]["precheck"] = "reports/precheck.json"
        if not precheck_only:
            manifest["formal_started"] = True
            write_json(manifest_path, manifest)
            training_started = perf_counter()
            train_and_save(trainer, arguments, script_args.dataset_name)
            write_json(directory / "reports/training.json", {
                "elapsed_seconds": perf_counter() - training_started,
                "completed_steps": trainer.state.global_step,
                "log_history": trainer.state.log_history,
            })
            manifest["outputs"]["training"] = "reports/training.json"
            shutil.make_archive(str(directory / "artifacts/checkpoint"), "zip", arguments.output_dir)
            manifest["outputs"]["checkpoint"] = "artifacts/checkpoint.zip"
        manifest["status"] = "succeeded"
    except KeyboardInterrupt:
        manifest["status"] = "interrupted"
        raise
    except Exception as error:
        stage = "formal_training" if manifest["formal_started"] else "automatic_precheck"
        manifest["diagnostics"].append({"stage": stage, "message": str(error)})
        manifest["status"] = "failed"
        raise
    finally:
        write_json(manifest_path, manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("precheck", "run"))
    parser.add_argument("--config", type=Path, default=ROOT / "conf/config.toml")
    parser.add_argument("--task", choices=("sft", "dpo", "reward", "kto", "distillation", "grpo", "rloo"))
    parser.add_argument("--max-steps", type=int, help="Cap formal training for an acceptance run.")
    parser.add_argument("--study", required=True, help="A new descriptive name for this experiment.")
    arguments = parser.parse_args(argv)
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", arguments.study):
        parser.error("Use one to three lowercase words separated by underscores in the study name.")
    with arguments.config.open("rb") as stream:
        config = tomllib.load(stream)
    if arguments.max_steps is not None and (arguments.max_steps < 1 or arguments.operation != "run"):
        parser.error("Use a positive --max-steps with run.")
    task = arguments.task or ("sft" if "recipes" in config else None)
    if task:
        from base.training_runs import run_training_recipe

        if task not in config.get("recipes", {}):
            parser.error(f"The configuration does not define a {task} recipe.")
        selected = [config["dataset"]["name"], config["model"]["name"], config["recipes"][task]["name"]]
        if not all(re.fullmatch(r"[a-z][a-z0-9_]*", component) for component in selected):
            parser.error("Expected descriptive component names in the configuration.")
        directory = ROOT.joinpath("experiment", *selected, arguments.study)
        directory.mkdir(parents=True, exist_ok=False)
        manifest_path = directory / "metadata/manifest.json"
        try:
            run_training_recipe(config, task, directory, precheck_only=arguments.operation == "precheck",
                                formal_steps=arguments.max_steps)
        except Exception as error:
            parser.exit(1, f"{error}\nRun record: {manifest_path}\n")
        print(manifest_path)
        return 0
    selected = [config[role]["name"] for role in ("dataset", "model", "task")]
    if selected != ["zen", "adapters", "training"]:
        parser.error("Expected the zen, adapters and training components in this recipe.")
    if arguments.max_steps is not None:
        config["training"]["max_steps"] = arguments.max_steps
    directory = ROOT.joinpath("experiment", *selected, arguments.study)
    directory.mkdir(parents=True, exist_ok=False)
    manifest_path = directory / "metadata/manifest.json"
    try:
        run(config, directory, precheck_only=arguments.operation == "precheck")
    except Exception as error:
        parser.exit(1, f"{error}\nRun record: {manifest_path}\n")
    print(manifest_path)
    return 0
