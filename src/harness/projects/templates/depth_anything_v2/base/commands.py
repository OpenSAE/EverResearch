"""Resolve public depth workflow options, precheck inputs, and dispatch science tasks."""

import argparse
from importlib import resources
import json
from math import isfinite
import os
from pathlib import Path
import tomllib

from .records import RunRecord, effective_options, read_run
from .tasks.precheck.check import demo_precheck, inference_inputs, inference_precheck

WORKFLOWS = {
    "image": ("image_files", "image_depth"),
    "metric": ("image_files", "metric_depth"),
    "video": ("video_files", "video_depth"),
    "pointcloud": ("image_files", "point_cloud"),
}


def settings():
    config = resources.files("depth_anything_v2.research.conf").joinpath("config.toml")
    return tomllib.loads(config.read_text(encoding="utf-8"))


def encoder_option(parser, defaults, encoders):
    parser.add_argument("--encoder", choices=encoders, default=defaults["encoder"])
    parser.add_argument("--load-from", type=Path)


def build_parser(defaults, encoders):
    parser = argparse.ArgumentParser(description="Depth Anything V2 research workflows")
    parser.add_argument("--workspace", type=Path, default=Path(os.getenv("DEPTH_ANYTHING_WORKSPACE", ".")))
    commands = parser.add_subparsers(dest="command", required=True)
    for command, (_, name) in WORKFLOWS.items():
        sub = commands.add_parser(command, help=name.replace("_", " "))
        media = "--video-path" if command == "video" else "--img-path"
        sub.add_argument(media, dest="source", type=Path, required=True)
        encoder_option(sub, defaults, encoders)
        if command == "pointcloud":
            sub.set_defaults(input_size=None)
        else:
            sub.add_argument("--input-size", type=int, default=defaults["input_size"])
        sub.add_argument("--study", default="depth_prediction")
        sub.add_argument("--outdir", type=Path, help="Export with the original input filenames")
        sub.add_argument("--precheck", action="store_true", help="Verify one input and its output without starting a run")
        if command in {"metric", "pointcloud"}:
            sub.add_argument("--max-depth", type=float, default=defaults["max_depth"])
        if command == "pointcloud":
            sub.add_argument("--focal-length-x", type=float, default=defaults["focal_length_x"])
            sub.add_argument("--focal-length-y", type=float, default=defaults["focal_length_y"])
        else:
            sub.add_argument("--pred-only", action="store_true")
            sub.add_argument("--grayscale", action="store_true")
        if command == "metric":
            sub.add_argument("--save-numpy", action="store_true")

    demo = commands.add_parser("demo", help="Launch the Gradio prediction interface")
    encoder_option(demo, defaults, encoders)
    demo.add_argument("--port", type=int)
    demo.add_argument("--precheck", action="store_true", help="Verify one demo image without serving the interface")
    commands.add_parser("train", add_help=False, help="Train the metric depth model")
    inspect = commands.add_parser("inspect", help="Read a saved run's settings and artifacts")
    inspect.add_argument("directory", type=Path)
    return parser


def default_checkpoint(args, defaults):
    name = f"depth_anything_v2_{args.encoder}.pth"
    if getattr(args, "max_depth", None) is not None:
        name = f"depth_anything_v2_metric_hypersim_{args.encoder}.pth"
    root = Path(os.getenv("DEPTH_ANYTHING_WEIGHTS", args.workspace / defaults["checkpoint_directory"]))
    return root / name


def predict(args, defaults, encoders):
    maximum = getattr(args, "max_depth", None)
    args.load_from = (args.load_from or default_checkpoint(args, defaults)).resolve()
    if args.command == "pointcloud" and not all(
        isfinite(length) and length > 0 for length in (args.focal_length_x, args.focal_length_y)
    ):
        raise ValueError("Focal lengths must be positive.")
    files = inference_inputs(args.source, args.load_from, args.input_size, maximum)
    dataset, task = WORKFLOWS[args.command]
    config = effective_options(args)
    config.update(dataset=dataset, model=encoders[args.encoder], task=task)
    config["source"] = str(args.source.resolve())
    if args.command == "video":
        from .tasks.video_depth.predict import predict as operation
    elif args.command == "pointcloud":
        from .tasks.point_cloud.export import predict as operation
    else:
        from .tasks.image_depth.predict import predict as operation
    record = None if args.precheck else RunRecord(args, config, files)
    try:
        model, report = inference_precheck(args, operation, files)
        if args.precheck:
            print(json.dumps({**config, "files": [str(path.resolve()) for path in files],
                              "precheck_report": report}, indent=2))
            return 0
        record.start_work(report)
        operation(args, model, files, record.output_path)
    except KeyboardInterrupt as error:
        if record is not None:
            record.finish("interrupted", error)
        raise
    except Exception as error:
        if record is not None:
            record.finish("failed", error)
        raise
    record.finish("succeeded")
    print(record.directory)
    return 0


def main(argv=None):
    config = settings()
    defaults = config["inference"]
    parser = build_parser(defaults, config["encoders"])
    args, remaining = parser.parse_known_args(argv)
    args.workspace = args.workspace.resolve()
    if args.command != "train" and remaining:
        parser.error(f"unrecognized arguments: {' '.join(remaining)}")
    try:
        if args.command == "train":
            from .tasks.training.train import main as train
            return train(remaining, args.workspace, defaults, config["training"], config["encoders"])
        if args.command == "inspect":
            print(json.dumps(read_run(args.directory), indent=2))
            return 0
        if args.command == "demo":
            from .tasks.demo.interface import launch

            examples = args.workspace / "assets/samples/images/files"
            args.load_from = (args.load_from or default_checkpoint(args, defaults)).resolve()
            model, report = demo_precheck(args, examples / "demo01.jpg")
            if args.precheck:
                print(json.dumps({**effective_options(args), "precheck_report": report}, indent=2))
            else:
                launch(model, examples, args.port)
            return 0
        return predict(args, defaults, config["encoders"])
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
