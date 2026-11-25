"""Purpose: Registration of public identification of selected model series.

Scope of application: Find a series of statements and their official build entrances when configures the selected model.
"""

from .convolution.small_cnn import specs as small_cnn
from .residual.residual18 import specs as resnet18

MODELS = {}
for series in (resnet18, small_cnn):
    for model in series.MODELS:
        if model.key in MODELS:
            raise ValueError(f"Model identification duplicate:{model.key}")
        MODELS[model.key] = model
