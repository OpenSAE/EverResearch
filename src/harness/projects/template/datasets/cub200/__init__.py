"""目的：声明 CUB-200 的项目入口。

适用范围：数据集登记、正式分类和预检。
"""

from .dataset import CLASSES, REQUIRES_ROOT, load, validate_config

__all__ = ["CLASSES", "REQUIRES_ROOT", "SUPPORTED_TASKS", "load", "validate_config"]
SUPPORTED_TASKS = frozenset({"classification"})
