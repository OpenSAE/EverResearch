"""Dispatch the MathVista public evaluation and preparation commands."""

import argparse
from importlib import import_module
import logging
import os
import runpy
import sys


COMMANDS = {
    "generate": ("mathvista.generation.generate_response", "Generate model responses"),
    "extract": ("mathvista.extraction.extract_answer", "Extract answers from responses"),
    "score": ("mathvista.scoring.calculate_score", "Score extracted answers"),
    "build-query": ("mathvista.generation.build_query", "Display the bundled query examples"),
    "caption-bard": ("mathvista.dataset.generate_caption_bard", "Generate Bard captions"),
    "caption-vision": ("mathvista.dataset.generate_caption_vision", "Generate ViT-GPT2 captions"),
    "ocr": ("mathvista.dataset.generate_text_easyocr", "Generate EasyOCR text"),
}


def main():
    parser = argparse.ArgumentParser(description="Run a MathVista evaluation stage.")
    subparsers = parser.add_subparsers(dest="stage", required=True)
    for name, (_, help_text) in COMMANDS.items():
        subparsers.add_parser(name, help=help_text, add_help=False)
    args, remaining = parser.parse_known_args()
    module, _ = COMMANDS[args.stage]
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper(), format="%(message)s")
    for name in ("httpx", "httpcore", "huggingface_hub", "filelock", "urllib3"):
        logging.getLogger(name).setLevel(logging.WARNING)
    if args.stage in {"generate", "extract", "score"}:
        import_module(module).main(remaining)
    else:
        sys.argv[1:] = remaining
        runpy.run_module(module, run_name="__main__")
