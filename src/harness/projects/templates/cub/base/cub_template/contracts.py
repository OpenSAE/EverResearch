"""Purpose: Define classification input and identity of the data set assigned to task.

Scope of application: Data, models and mission access for this reference item. Specific indicators are the responsibility of the task..
"""

from dataclasses import dataclass
from typing import Callable

from torch.utils.data import Dataset


@dataclass(frozen=True)
class ClassificationInputs:
    train: Dataset
    test: Dataset
    fixed_train: Dataset
    identity: dict
    classes: int


def validate_rgb_config(config):
    size = config["image_size"]
    if type(size) is not int or size < 32:
        raise ValueError("dataset.image_size It must be at least. 32 Integer number")


@dataclass(frozen=True)
class EvaluationResult:
    """The result of the task returned, written by the running layer on the list."""

    summary: dict


class TaskModule:
    """Project task interface. Parameter check ahead of model and data loading."""

    def validate_cfg(self, cfg, operation):
        raise NotImplementedError

    def run(self, request) -> EvaluationResult:
        raise NotImplementedError


@dataclass(frozen=True)
class PerformanceWorkload:
    samples: int
    scope: str
    make_batches: Callable
    forward: Callable
