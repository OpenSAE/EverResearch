"""Turn AgentFlow's YAML settings into the Flow-GRPO launcher arguments."""

import argparse
import json
import os
from pathlib import Path
from string import Template
import subprocess
import sys

import yaml

from agentflow.project_paths import config_directory


def main():
    parser = argparse.ArgumentParser(description="Run Flow-GRPO with AgentFlow settings.")
    parser.add_argument("--config", type=Path, default=config_directory() / "config.yaml")
    parser.add_argument("--preview", action="store_true", help="Show arguments without starting Ray.")
    parser.add_argument("--precheck", action="store_true", help="Read one sample from each input file.")
    parser.add_argument("overrides", nargs="*", metavar="KEY=VALUE")
    args = parser.parse_args()
    try:
        with args.config.open(encoding="utf-8") as stream:
            config = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        parser.error(str(exc))

    env = os.environ.copy()
    for key, value in config.get("env", {}).items():
        if key == "OPENAI_API_KEY" and value == "YOUR_ONENAI_API":
            continue
        env[key] = str(value)
    if "BASE_DATA_DIR" in os.environ:
        env["BASE_DATA_DIR"] = os.environ["BASE_DATA_DIR"]
    elif env.get("BASE_DATA_DIR") == "assets/prepared_data/training_inputs/files":
        env["BASE_DATA_DIR"] = str(args.config.resolve().parent.parent / env["BASE_DATA_DIR"])
    settings = {}
    for key, value in config.get("python_args", {}).items():
        settings[key] = Template(value).safe_substitute(env) if isinstance(value, str) else str(value)
    for override in args.overrides:
        key, separator, value = override.partition("=")
        if not key or not separator:
            parser.error(f"expected KEY=VALUE, received {override}")
        settings[key] = value
    command = [sys.executable, "-m", "agentflow.verl"]
    command.extend(f"{key}={value}" for key, value in settings.items())
    if args.preview:
        print(f"Configuration {args.config}")
        print("\n".join(command))
        return
    try:
        from agentflow.precheck.training_inputs import check_training_inputs

        checks = check_training_inputs(settings)
    except (ImportError, KeyError, OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    if args.precheck:
        print(json.dumps(checks))
        return
    raise SystemExit(subprocess.run(command, env=env).returncode)


if __name__ == "__main__":
    main()
