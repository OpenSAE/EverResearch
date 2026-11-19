"""任务标识和任务类，供项目登记入口读取。"""

from .classification.task import ClassificationTask
from .precheck.task import PrecheckTask

TASKS = {"classification": ClassificationTask, "precheck": PrecheckTask}
