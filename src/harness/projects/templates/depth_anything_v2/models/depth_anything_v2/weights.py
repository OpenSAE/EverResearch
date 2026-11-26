"""Construct the relative and metric encoder variants used by the research tasks."""

import torch

from .dpt import DepthAnythingV2
from .metric import MetricDepthAnythingV2


ENCODERS = {
    "vits": (64, [48, 96, 192, 384]),
    "vitb": (128, [96, 192, 384, 768]),
    "vitl": (256, [256, 512, 1024, 1024]),
    "vitg": (384, [1536, 1536, 1536, 1536]),
}


def build_model(encoder, max_depth=None):
    features, channels = ENCODERS[encoder]
    options = {"encoder": encoder, "features": features, "out_channels": channels}
    if max_depth is None:
        return DepthAnythingV2(**options)
    return MetricDepthAnythingV2(**options, max_depth=max_depth)


def load_model(encoder, checkpoint, max_depth=None):
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    model = build_model(encoder, max_depth)
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    return model.to(device).eval()
