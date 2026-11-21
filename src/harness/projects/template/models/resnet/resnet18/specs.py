"""Purpose: Same ResNet18 Series of declarations for header variants that can be selected independently.

Scope of application: model registration and formulation selection, with two variants sharing the same construction and validation.
"""

from ...build import ModelSpec
from . import model

MODELS = (
    ModelSpec(
        "resnet18_mlp", model.CLASSES, model.build, model.validate_config, {"hidden_dim": 256}
    ),
    ModelSpec(
        "resnet18_mlp_small", model.CLASSES, model.build, model.validate_config, {"hidden_dim": 16}
    ),
)
