"""Expose the public CogVideoX generation, precheck and result-reading commands."""

import argparse
from importlib.resources import files
import json
import logging
from pathlib import Path

from cogvideo_precheck.task import check_generation

from .records import publish_generation, read_generation


def add_generation_arguments(parser):
    parser.add_argument("--config", type=Path, help="Read a JSON generation settings file")
    parser.add_argument("--prompt", help="Text description of the video")
    parser.add_argument("--model_path", help="Hugging Face model ID or local model directory")
    parser.add_argument("--image_or_video_path", help="Conditioning image or video for i2v or v2v")
    parser.add_argument("--lora_path", help="Directory containing adapter weights")
    parser.add_argument("--lora_rank", type=int)
    parser.add_argument("--output_path", help="Export the video directly to this path")
    parser.add_argument("--guidance_scale", type=float)
    parser.add_argument("--num_inference_steps", type=int)
    parser.add_argument("--num_frames", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", type=int)
    parser.add_argument("--num_videos_per_prompt", type=int)
    parser.add_argument("--generate_type", choices=("t2v", "i2v", "v2v"))
    parser.add_argument("--dtype", choices=("bfloat16", "float16"))
    parser.add_argument("--seed", type=int)


def generation_settings(arguments):
    settings = json.loads(files("cogvideo_defaults").joinpath("config.json").read_text(encoding="utf-8"))
    defaults = settings["generation"]
    if arguments.config is not None:
        document = json.loads(arguments.config.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("Configuration must be a JSON object.")
        overrides = document.get("generation", document)
        if not isinstance(overrides, dict):
            raise ValueError("Generation settings must be a JSON object.")
        unknown = set(overrides) - defaults.keys() - {"prompt"}
        if unknown:
            raise ValueError(f"Unknown generation settings: {', '.join(sorted(unknown))}")
        defaults.update(overrides)
    defaults.update({
        key: getattr(arguments, key)
        for key in (*defaults.keys(), "prompt")
        if getattr(arguments, key) is not None
    })
    return check_generation(defaults, settings["catalogs"])


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate video with CogVideoX")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("generate", help="Generate a video and save its result")
    add_generation_arguments(run_parser)
    run_parser.add_argument("--workspace", type=Path, default=Path.cwd())
    run_parser.add_argument("--purpose", default="generated_video")
    run_parser.add_argument("--execution", default="initial_generation")
    add_generation_arguments(commands.add_parser("precheck", help="Show effective options without loading weights"))
    inspect = commands.add_parser("inspect", help="Open a generation run by directory")
    inspect.add_argument("run", type=Path)
    arguments = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)

    effective = None
    try:
        if arguments.command == "inspect":
            result = read_generation(arguments.run)
        else:
            effective = generation_settings(arguments)
            if arguments.command == "precheck":
                result = effective
            else:
                missing = effective["resources"]["missing_modules"]
                if missing:
                    raise ValueError(f"Install the missing inference packages: {', '.join(missing)}")
                result = run_generation(arguments, effective)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"cogvideo: {error}\n")
    print(json.dumps(result, indent=2))
    return int(arguments.command == "precheck" and bool(effective["resources"]["missing_modules"]))


def run_generation(arguments, effective):
    import torch

    from cogvideo_tasks.task import generate_video

    generation = effective["generation"].copy()
    output_path = generation.pop("output_path")
    dtype = torch.float16 if generation.pop("dtype") == "float16" else torch.bfloat16

    def generate(path):
        generate_video(**generation, dtype=dtype, output_path=str(path), log_resolution=False)

    if output_path is not None:
        generate(output_path)
        return {"output": str(Path(output_path).resolve())}
    run = publish_generation(arguments.workspace.resolve(), arguments.purpose, arguments.execution, effective, generate)
    return {"run": str(run), "output": str(run / "artifacts" / "generated_video.mp4")}


def legacy_generate():
    """Keep the standalone inference flag interface and its default output filename."""
    import sys

    return main(["generate", "--output_path", "./output.mp4", *sys.argv[1:]])
