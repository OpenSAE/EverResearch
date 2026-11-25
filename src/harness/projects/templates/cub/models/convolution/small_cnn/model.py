"""Purpose: To provide access to ResNet18 Light image classification model for formula swaps.

Scope: 200 Category RGB Example of image classification and offline component extensions.
"""

from torch import nn

CLASSES = 200


def validate_config(config):
    channels = config.get("channels", 16)
    if type(channels) is not int or channels < 1:
        raise ValueError("model.channels Must be positive integer")
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
