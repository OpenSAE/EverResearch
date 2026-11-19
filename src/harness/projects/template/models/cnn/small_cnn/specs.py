"""目的：声明独立的轻量 CNN 模型。

适用范围：通过模型登记选择当前 CNN 系列。
"""

from ...build import ModelSpec
from . import model

MODELS = (
    ModelSpec("small_cnn", model.CLASSES, model.build, model.validate_config, {"channels": 16}),
)
