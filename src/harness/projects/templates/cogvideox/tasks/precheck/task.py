"""Validate CogVideoX inference arguments and report the selected components."""

from importlib.util import find_spec
from pathlib import Path
from urllib.parse import urlsplit

from cogvideo_generation.pipeline import resolve_resolution
from cogvideo_inputs.media import validate_conditioning


def check_generation(options, catalogs):
    """Resolve the original defaults and report available resources without loading weights."""
    prompt = options.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Supply a text prompt with --prompt or the configuration file.")
    generation_type = options["generate_type"]
    if generation_type not in {"t2v", "i2v", "v2v"}:
        raise ValueError("Generation type must be t2v, i2v or v2v.")
    if options["dtype"] not in {"bfloat16", "float16"}:
        raise ValueError("Use bfloat16 or float16 for dtype.")
    for key in ("num_inference_steps", "num_frames", "fps", "num_videos_per_prompt", "width", "height"):
        value = options[key]
        if value is None and key in {"width", "height"}:
            continue
        if type(value) is not int or value <= 0:
            raise ValueError(f"{key} must be a positive integer.")
    model_path = options["model_path"]
    if not isinstance(model_path, str) or not model_path.strip():
        raise ValueError("Supply a Hugging Face model ID or local checkpoint directory.")
    local_model = Path(model_path).expanduser()
    if local_model.is_dir():
        if not (local_model / "model_index.json").is_file():
            raise ValueError(f"Missing Diffusers model_index.json in {local_model}")
        model_path = str(local_model.resolve())
    elif local_model.is_absolute() or model_path.startswith(("./", "../", "~")):
        raise ValueError(f"Model directory does not exist: {model_path}")
    source = options["image_or_video_path"]
    if source is not None and not isinstance(source, str):
        raise ValueError("The conditioning source must be a media path or URL.")
    dataset = validate_conditioning(generation_type, source)
    if generation_type != "t2v" and urlsplit(source).scheme not in {"http", "https"}:
        source = str(Path(source).expanduser().resolve())
    height, width = resolve_resolution(model_path, generation_type, options["width"], options["height"])
    model_basename = model_path.rstrip("/").rsplit("/", 1)[-1].lower()
    if (generation_type == "i2v") != model_basename.endswith("-i2v"):
        raise ValueError(f"Model {model_basename} is incompatible with {generation_type}.")
    model = next(key for key, name in catalogs["model"].items() if name.lower() == model_basename)
    effective_options = {
        **options, "height": height, "width": width, "model_path": model_path,
        "image_or_video_path": source,
    }
    missing = [
        module for module in ("torch", "diffusers", "transformers", "accelerate", "imageio", "imageio_ffmpeg")
        if find_spec(module) is None
    ]
    cuda_available = False
    if "torch" not in missing:
        import torch

        cuda_available = torch.cuda.is_available()
    return {
        "component_paths": {"dataset": dataset, "model": model, "task": "video_generation"},
        "generation": effective_options,
        "resources": {
            "model_source": "local_directory" if local_model.is_dir() else "hub_id",
            "missing_modules": missing,
            "cuda_available": cuda_available,
        },
    }
