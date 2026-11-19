"""目的：定义数据集交给任务的分类输入与身份。

适用范围：本参考项目的数据、模型和任务接入。具体指标由任务负责。
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
        raise ValueError("dataset.image_size 必须是至少 32 的整数")


@dataclass(frozen=True)
class EvaluationResult:
    """任务返回的结果，由运行层写入清单。"""

    summary: dict


class TaskModule:
    """项目任务接口。参数检查先于模型和数据加载。"""

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
