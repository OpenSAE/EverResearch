"""Job identification and task class for access to project registration portals."""

from .classification.task import ClassificationTask
from .precheck.task import PrecheckTask

TASKS = {"classification": ClassificationTask, "precheck": PrecheckTask}
