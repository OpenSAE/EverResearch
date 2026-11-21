"""Load the VGGT model and set inference precision for the demos."""

import torch

from vggt.models.geometry_transformer import VGGT
from vggt.utils.pose_enc import pose_encoding_to_extri_intri


WEIGHTS_URL = "https://huggingface.co/facebook/VGGT-1B/resolve/main/model.pt"


def load_demo_model(device):
    """Load the published demo checkpoint and prepare it for inference."""
    model = VGGT()
    model.load_state_dict(torch.hub.load_state_dict_from_url(WEIGHTS_URL, map_location="cpu"))
    return model.eval().to(device)


def cuda_dtype(device):
    """Choose CUDA autocast precision or return None on CPU."""
    device = torch.device(device)
    if device.type != "cuda":
        return None
    return torch.bfloat16 if torch.cuda.get_device_capability(device)[0] >= 8 else torch.float16


@torch.inference_mode()
def predict_scene(model, images):
    """Return viewer predictions with the batch dimension removed from tensors."""
    dtype = cuda_dtype(images.device)
    with torch.autocast("cuda", dtype=dtype, enabled=dtype is not None):
        predictions = model(images)

    extrinsic, intrinsic = pose_encoding_to_extri_intri(predictions["pose_enc"], images.shape[-2:])
    predictions["extrinsic"] = extrinsic
    predictions["intrinsic"] = intrinsic

    for key, value in predictions.items():
        if isinstance(value, torch.Tensor):
            predictions[key] = value.cpu().numpy().squeeze(0)
    return predictions
