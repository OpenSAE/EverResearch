"""Dispatch VGGT's command-line applications from source and installed packages."""

import argparse
from importlib import import_module
import sys


COMMANDS = {
    "colmap": ("vggt.colmap.export", "Export a COLMAP reconstruction"),
    "gradio": ("vggt.viewer.gradio_viewer", "Open the Gradio upload interface"),
    "viser": ("vggt.viewer.viser_viewer", "Display reconstruction in Viser"),
    "train": ("vggt.runtime.launch", "Fine-tune or validate the model"),
    "read-colmap": ("vggt.colmap.records", "Unpack a recorded COLMAP reconstruction"),
    "precheck": ("vggt.precheck.gate", "Check local resources for a scene"),
}


def main():
    parser = argparse.ArgumentParser(description="VGGT camera and scene reconstruction")
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command, (_, description) in COMMANDS.items():
        subcommands.add_parser(command, add_help=False, help=description)
    args, remaining = parser.parse_known_args()
    module, _ = COMMANDS[args.command]
    sys.argv[1:] = remaining
    import_module(module).main()
