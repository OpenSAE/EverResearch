"""Validate selected scene inputs and training resources before model work."""

import argparse
from pathlib import Path
from typing import Sequence

from PIL import Image


def check_images(image_paths: Sequence, *, shared_camera=False):
    """Decode one representative frame and verify shared-camera shapes."""
    if not image_paths:
        raise ValueError("No images found. Provide a directory containing at least one RGB image.")
    reference_size = None
    for index, path in enumerate(image_paths if shared_camera else image_paths[:1]):
        try:
            with Image.open(path) as image:
                reference_size = reference_size or image.size
                if image.size != reference_size:
                    raise ValueError("--shared_camera requires images with the same original width and height.")
                if index == 0:
                    image.load()
        except OSError as error:
            raise ValueError(f"Cannot read image {path}: {error}") from error
    return 1


def check_training(config):
    """Check the selected input roots and distributed device before initialization."""
    phases = ("val",) if config.get("mode", "train") == "val" else ("train", "val")
    for phase in phases:
        source = config.data.get(phase)
        if source is None:
            continue
        for reader in source.dataset.dataset_configs:
            for setting in ("CO3D_DIR", "CO3D_ANNOTATION_DIR", "VKitti_DIR"):
                if setting in reader:
                    directory = reader[setting]
                    if not directory or not Path(directory).is_dir():
                        raise ValueError(f"{phase} {setting} is not a readable directory: {directory!r}")

    import torch

    if config.get("device", "cuda") == "cuda" and not torch.cuda.is_available():
        raise ValueError("The training recipe requires a CUDA device.")
    checkpoint = config.checkpoint.get("resume_checkpoint_path")
    if checkpoint and "://" not in str(checkpoint) and not Path(checkpoint).is_file():
        raise ValueError(f"The training checkpoint does not exist: {checkpoint}")


def main():
    parser = argparse.ArgumentParser(description="Check the inputs to a VGGT scene reconstruction")
    parser.add_argument("--image-folder", required=True, type=Path)
    parser.add_argument("--shared-camera", action="store_true")
    args = parser.parse_args()
    try:
        paths = sorted(path for path in args.image_folder.glob("*") if path.is_file())
        checked = check_images(paths, shared_camera=args.shared_camera)
    except ValueError as error:
        parser.error(str(error))
    print(f"Decoded {checked} representative image from {len(paths)} inputs.")
