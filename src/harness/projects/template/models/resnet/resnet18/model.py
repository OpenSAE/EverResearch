"""目的：用 ResNet18 提取图像特征，以 MLP 输出 200 类 logits。

适用范围：正式训练、预检和性能比较，使用本地随机初始化。
"""

from torch import nn
from torchvision.models import resnet18


CLASSES = 200


def validate_config(config):
    hidden_dim = config["hidden_dim"]
    if type(hidden_dim) is not int or hidden_dim < 1:
        raise ValueError("model.hidden_dim 必须为正整数")
    if config.get("initialization", "random") != "random":
        raise ValueError("此模型实现使用随机初始化。复跑预训练实验时，请使用清单记录的对应源码")
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
