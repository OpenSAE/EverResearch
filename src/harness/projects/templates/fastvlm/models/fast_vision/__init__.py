"""Load a FastVLM PyTorch checkpoint and place its components on one device."""
import json
from pathlib import Path


def load_checkpoint(model_path, model_base, device):
    import torch
    from llava.mm_utils import get_model_name_from_path
    from llava.model.builder import load_pretrained_model

    if device == "auto":
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    if device == "mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS is unavailable. Select --device cuda or --device cpu.")
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA is unavailable. Select --device mps or --device cpu.")

    model_name = get_model_name_from_path(model_path)
    config_path = Path(model_path) / "config.json"
    if "llava" not in model_name.lower() and config_path.is_file():
        # The builder historically dispatches by name. Use the checkpoint's
        # declared family when the user stores a FastVLM checkpoint under an alias.
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if config.get("model_type") == "llava_qwen2":
            model_name = "llava-qwen"

    dtype = torch.float32 if device == "cpu" else torch.float16
    tokenizer, model, processor, _ = load_pretrained_model(
        model_path, model_base, model_name, device=device,
        device_map={"": device}, torch_dtype=dtype,
    )
    if processor is None:
        raise ValueError("The checkpoint must include a LLaVA vision tower.")
    model.eval()
    return tokenizer, model, processor, device
