"""目的：在同一 ResNet18 系列声明可独立选择的分类头变体。

适用范围：模型登记和配方选择，两个变体共用同一构建与验证实现。
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
