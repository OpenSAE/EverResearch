"""目的：生成符合 CUB 分类输入接口的离线检查样本。

适用范围：CUB-200 分类的离线预检、性能演练和功能回归，配方通过 synthetic 选择。
"""

import torch
from torch.utils.data import TensorDataset


from ...contracts import ClassificationInputs, validate_rgb_config as validate_config
from . import CLASSES, SUPPORTED_TASKS

__all__ = ["CLASSES", "REQUIRES_ROOT", "SUPPORTED_TASKS", "load", "validate_config"]

REQUIRES_ROOT = False


def load(config, seed):
    """返回训练、测试、确定性训练视图和合成输入身份。"""
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
