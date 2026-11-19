"""目的：提供可与 ResNet18 配方互换的轻量图像分类模型。

适用范围：200 类 RGB 图像分类及离线的组件扩展示例。
"""

from torch import nn

CLASSES = 200


def validate_config(config):
    channels = config.get("channels", 16)
    if type(channels) is not int or channels < 1:
        raise ValueError("model.channels 必须为正整数")
    return channels


def build(config):
    channels = validate_config(config)
    return nn.Sequential(
        nn.Conv2d(3, channels, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Linear(channels, CLASSES),
    )
