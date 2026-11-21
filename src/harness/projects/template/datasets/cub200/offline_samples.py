"""Purpose: Generate matches CUB Samples of offline check for classification input interfaces.

Scope: CUB-200 Offline precheck, performance exercise and functional regression of categories, formulae passed synthetic Selection.
"""

import torch
from torch.utils.data import TensorDataset


from ...contracts import ClassificationInputs, validate_rgb_config as validate_config
from . import CLASSES, SUPPORTED_TASKS

__all__ = ["CLASSES", "REQUIRES_ROOT", "SUPPORTED_TASKS", "load", "validate_config"]

REQUIRES_ROOT = False


def load(config, seed):
    """Return training, testing, definitive training view and synthesis of identity input."""
    size = config["image_size"]
    generator = torch.Generator().manual_seed(seed)
    images = torch.randn(12, 3, size, size, generator=generator)
    labels = torch.arange(len(images)) % CLASSES
    train = TensorDataset(images[:8], labels[:8])
    return ClassificationInputs(
        train,
        TensorDataset(images[8:], labels[8:]),
        train,
        {"dataset": "synthetic", "seed": seed, "train": 8, "test": 4},
        CLASSES,
    )
