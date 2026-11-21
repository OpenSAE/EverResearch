"""Parse the public FastVLM command and dispatch configuration, inference or readback."""
import argparse
import json
import math
import sys

from .records import read_result, valid_dataset, valid_subname
from .runtime import resolve_config, run


def _parser():
    parser = argparse.ArgumentParser(description="Generate an answer for one image with FastVLM.")
    parser.add_argument("--model-path", help="Checkpoint directory or Hugging Face repository.")
    parser.add_argument("--model-base", help="Optional base checkpoint for adapter weights.")
    parser.add_argument("--image-file", help="Path to an input image.")
    parser.add_argument("--dataset", help="Source dataset name for result grouping, such as coco_val.")
    parser.add_argument("--prompt", help="Prompt for the vision-language model.")
    parser.add_argument("--conv-mode", help="LLaVA conversation template.")
    parser.add_argument("--temperature", type=float, help="Sampling temperature. Zero uses deterministic decoding.")
    parser.add_argument("--top_p", "--top-p", dest="top_p", type=float, help="Nucleus sampling threshold.")
    parser.add_argument("--num_beams", "--num-beams", dest="num_beams", type=int, help="Beam count.")
    parser.add_argument("--max-new-tokens", type=int, help="Maximum number of generated tokens.")
    parser.add_argument("--device", choices=("auto", "mps", "cuda", "cpu"), help="PyTorch device.")
    parser.add_argument("--subname", help="Experiment name, as one to three lowercase words joined with underscores.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--precheck", action="store_true", help="Check one image, checkpoint, and one-token prediction.")
    modes.add_argument("--show-config", action="store_true", help="Print resolved settings and exit before loading resources.")
    modes.add_argument("--read-result", metavar="MANIFEST", help="Print a saved prediction as JSON.")
    return parser


def _validate(config):
    if not valid_dataset(config["dataset"]):
        raise ValueError("--dataset must use lowercase letters, digits and single underscores, such as coco_val.")
    if not valid_subname(config["subname"]):
        raise ValueError("--subname must be one to three lowercase words joined with underscores, such as describe_image.")
    if not math.isfinite(config["temperature"]) or config["temperature"] < 0:
        raise ValueError("--temperature must be a finite nonnegative number.")
    if config["top_p"] is not None and not 0 < config["top_p"] <= 1:
        raise ValueError("--top-p must be greater than zero and at most one.")
    if config["num_beams"] < 1 or config["max_new_tokens"] < 1:
        raise ValueError("--num-beams and --max-new-tokens must be positive integers.")


def predict(args):
    """Compatibility callable used by the original predict.py script."""
    config = resolve_config({key: val for key, val in vars(args).items() if val is not None})
    _validate(config)
    _run_and_print(config)


def _run_and_print(config):
    if config["image_file"] is None:
        raise ValueError("--image-file is required for inference.")
    answer, manifest = run(config)
    print(answer)
    print(f"Run manifest: {manifest}", file=sys.stderr)


def main(argv=None):
    parser = _parser()
    options = vars(parser.parse_args(argv))
    show_config = options.pop("show_config")
    manifest = options.pop("read_result")
    precheck_only = options.pop("precheck")
    try:
        if manifest is not None:
            print(json.dumps(read_result(manifest), ensure_ascii=False, indent=2))
            return
        config = resolve_config({key: val for key, val in options.items() if val is not None})
        _validate(config)
        if show_config:
            print(json.dumps(config, ensure_ascii=False, indent=2))
            return
        if precheck_only:
            if config["image_file"] is None:
                raise ValueError("--image-file is required for precheck.")
            print(json.dumps(run(config, precheck_only=True), ensure_ascii=False, indent=2))
            return
        _run_and_print(config)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
