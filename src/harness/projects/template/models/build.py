"""目的：按系列声明检查参数和构建模型。

适用范围：当前模板的具名模型变体，共用登记和构建入口。
"""

from dataclasses import dataclass, field
from typing import Callable, Mapping


@dataclass(frozen=True)
class ModelSpec:
    key: str
    CLASSES: int
    factory: Callable
    validator: Callable
    defaults: Mapping[str, int] = field(default_factory=dict)

    def resolve_config(self, config):
        actual = {**self.defaults, **config}
        self.validator(actual)
        return actual

    def validate_config(self, config):
        self.resolve_config(config)

    def build(self, config):
        return self.factory({**self.defaults, **config})
