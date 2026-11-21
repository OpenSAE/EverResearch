"""Run SAM 2 research commands from a source checkout."""
import sys
from importlib import import_module
from pathlib import Path
from runpy import run_path

COMMANDS = {
    "benchmark": ("sam2.benchmarking.benchmark", "main"),
    "precheck": ("sam2.precheck.command", "main"),
    "image": ("sam2.tasks.image_inference", "main"),
    "video": ("sam2.video.inference", "main"),
    "train": ("training.train", "cli"),
    "evaluate": ("sam2.evaluation.evaluator", "main"),
}


def enable_checkout_imports():
    imports = Path(__file__).parent / "base" / "segment_anything" / "imports.py"
    run_path(str(imports))["install_public_imports"]()


def main():
    enable_checkout_imports()
    command = sys.argv.pop(1) if sys.argv[1:2] and sys.argv[1] in COMMANDS else "image"
    module, function = COMMANDS[command]
    getattr(import_module(module), function)()


if __name__ == "__main__":
    main()
