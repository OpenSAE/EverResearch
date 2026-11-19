"""目的：将配置中的组件标识连接到本地正式实现。

适用范围：预检、训练和性能比较共享的组件选择。项目维护者在此登记实现。
"""

from .datasets.plugins import DATASETS
from .models.plugins import MODELS
from .tasks.plugins import TASKS

COMPONENTS = {"dataset": DATASETS, "model": MODELS, "task": TASKS}


def resolve(kind, name):
    choices = COMPONENTS[kind]
    if not isinstance(name, str) or name not in choices:
        raise ValueError(f"{kind}.name={name!r} 未登记，可选：{', '.join(sorted(choices))}")
    return choices[name]
