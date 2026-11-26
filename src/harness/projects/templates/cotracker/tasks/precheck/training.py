"""Reject missing training input and output paths before spawning distributed workers."""

from pathlib import Path


def check_training_paths(args, parser):
    if not args.dataset_root or not Path(args.dataset_root).is_dir():
        parser.error("--dataset_root must point to the directory containing the training and evaluation data")
    if not args.ckpt_path:
        parser.error("--ckpt_path must name the directory for checkpoints and training outputs")
