"""Purpose: To formally connect the component identifier in the configuration to the local location.

The project maintainer registers here..
"""

from .datasets.plugins import DATASETS
from .models.plugins import MODELS
from .tasks.plugins import TASKS

COMPONENTS = {"dataset": DATASETS, "model": MODELS, "task": TASKS}


def resolve(kind, name):
    choices = COMPONENTS[kind]
    if not isinstance(name, str) or name not in choices:
        raise ValueError(f"{kind}.name={name!r} Unregistered, optional:{', '.join(sorted(choices))}")
    return choices[name]
