"""Purpose: To check parameters and build models by series of statements.

Scope of application: Name model variant of the current template, common registration and build access.
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
