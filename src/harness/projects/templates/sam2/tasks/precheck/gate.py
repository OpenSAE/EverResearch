"""Check input resources and task compatibility before research commands run."""
from pathlib import Path

import torch

from sam2.example_images.source import open_rgb
from sam2.utils.misc import list_jpeg_frames


def require_file(path, description):
    resource = Path(path)
    if not resource.is_file():
        raise FileNotFoundError(f"{description} not found: {resource}")
    return resource


def require_directory(path, description):
    resource = Path(path)
    if not resource.is_dir():
        raise FileNotFoundError(f"{description} not found: {resource}")
    return resource


def check_image(settings):
    checkpoint = require_file(settings["checkpoint"], "Model checkpoint")
    image_path = require_file(settings["image"], "Input image")
    image = open_rgb(image_path)
    width, height = image.size
    for x, y, _ in settings["points"]:
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"Point ({x}, {y}) is outside the {width}x{height} image")
    try:
        device = torch.device(settings["device"])
    except RuntimeError as exc:
        raise ValueError(str(exc)) from exc
    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA is unavailable. Select --device cpu or use a CUDA installation.")
    return checkpoint, image, device


def check_video(checkpoint, images, masks, video_names):
    require_file(checkpoint, "Model checkpoint")
    image_root = require_directory(images, "Video frames")
    mask_root = require_directory(masks, "Prompt masks")
    if not video_names:
        raise ValueError(f"No video clips found in {image_root}")
    for name in video_names:
        if not name or Path(name).name != name or name in {".", ".."}:
            raise ValueError(f"Invalid video clip name: {name!r}")
        if not list_jpeg_frames(require_directory(image_root / name, "Clip frames")):
            raise ValueError(f"No JPEG frames found for {name}")
        prompt_root = require_directory(mask_root / name, "Clip prompt masks")
        if next(prompt_root.rglob("*.png"), None) is None:
            raise ValueError(f"No PNG prompt masks found for {name}")
