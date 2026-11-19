"""目的：登记已选模型系列的公开标识。

适用范围：配置选取模型时查找系列声明及其正式构建入口。
"""

from .cnn.small_cnn import specs as small_cnn
from .resnet.resnet18 import specs as resnet18

MODELS = {}
for series in (resnet18, small_cnn):
    for model in series.MODELS:
        if model.key in MODELS:
            raise ValueError(f"模型标识重复：{model.key}")
        MODELS[model.key] = model
