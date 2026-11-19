"""目的：提供图像分类任务的公开入口。

适用范围：由组件登记选择分类操作和兼容规则。
"""

from .task import ClassificationTask

__all__ = ["ClassificationTask"]
