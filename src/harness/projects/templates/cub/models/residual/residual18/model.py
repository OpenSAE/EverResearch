"""Purpose: Use ResNet18 Extract image characteristics as MLP Outputs 200 Category logits.

Scope of application: formal training, precheck and performance comparisons, using local random initialization.
"""

from torch import nn
from torchvision.models import resnet18


CLASSES = 200


def validate_config(config):
    hidden_dim = config["hidden_dim"]
    if type(hidden_dim) is not int or hidden_dim < 1:
        raise ValueError("model.hidden_dim Must be positive integer")
    if config.get("initialization", "random") != "random":
        raise ValueError("This model is used for random initialization. When reruning pre-training experiments, use the corresponding source code of the inventory record.")
    return hidden_dim


def build(config):
    hidden_dim = validate_config(config)
    model = resnet18(weights=None)
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, hidden_dim),
        nn.ReLU(),
        nn.Linear(hidden_dim, CLASSES),
    )
    return model
