"""Resolve and load image or video conditioning for CogVideoX inference."""

from pathlib import Path
from urllib.parse import urlsplit


def validate_conditioning(generation_type, source):
    """Validate the input reference without opening local media or contacting a URL."""
    if generation_type == "t2v":
        return "prompts"
    if not source:
        raise ValueError(f"{generation_type} requires --image_or_video_path")
    if urlsplit(source).scheme not in {"http", "https"} and not Path(source).expanduser().is_file():
        raise ValueError(f"Conditioning file does not exist: {source}")
    return "image_inputs" if generation_type == "i2v" else "video_inputs"


def read_conditioning(generation_type, source):
    """Read conditioning through the same Diffusers image and video readers as the CLI demo."""
    if generation_type == "i2v":
        from diffusers.utils import load_image

        return load_image(image=source), None
    if generation_type == "v2v":
        from diffusers.utils import load_video

        return None, load_video(source)
    return None, None
