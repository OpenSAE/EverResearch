"""Launch DINOv2 research workflows from a source checkout.

Installed users can also run the original dinov2.run module names.
"""

import argparse
import json
from pathlib import Path
import runpy
import sys

from base.checkout import use_checkout_packages


COMMANDS = {
    "train": "dinov2.run.train.train",
    "knn": "dinov2.run.eval.knn",
    "linear": "dinov2.run.eval.linear",
    "logistic": "dinov2.run.eval.log_regression",
    "cell-knn": "dinov2.run.eval.cell_dino.knn",
    "cell-linear": "dinov2.run.eval.cell_dino.linear",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=[*COMMANDS, "precheck"])
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    use_checkout_packages()
    if args.command == "precheck":
        from dinov2.precheck.task import check_backbone

        precheck = argparse.ArgumentParser(prog=f"{parser.prog} precheck")
        precheck.add_argument("--config-file", default="eval/vits14_pretrain")
        precheck.add_argument("--image", type=Path)
        options = precheck.parse_args(args.arguments)
        try:
            report = check_backbone(options.config_file, options.image)
        except (ValueError, OSError) as error:
            precheck.error(str(error))
        print(json.dumps(report, indent=2))
        return
    sys.argv[1:] = args.arguments
    runpy.run_module(COMMANDS[args.command], run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
