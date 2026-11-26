import enum
import os
from importlib import import_module
from typing import Sequence

import yaml

from evaluation.configuration import load_configuration
from evaluation.schemas import TaskBase, JailbreakBase


class EvalMode(enum.Enum):
    GENERATION = "generation"
    CLASSIFICATION = "classification"


def load_evaluation_tasks(
    mode: EvalMode, tasks: list[str], limit: bool = False, flex: bool = False, hparam_overrides: dict = None
) -> Sequence[TaskBase]:
    """
    Load the evaluators for the given tasks.
    Args:
        mode: Evaluation mode, either generation or classification.
            it will be used to load the tasks from the correct directory.

        tasks: List of tasks to evaluate the model on.
            each task can be xxx or xxx:yyy where xxx is the task name and yyy is the task config file name.
            if yyy is not provided, it will be assumed as xxx/default.yaml.

    Returns:
        List of evaluators.
    """
    evaluation_tasks = []
    configuration = load_configuration("config.yaml")
    presets = load_configuration(configuration["task_presets"][mode.value])
    for task in tasks:
        # split by ":" to get the task name and the config file name.
        # if the config file name is not provided, it will be assumed as task/default.yaml.
        task_name = task if ":" not in task else task.split(":")[0]
        config_file_name = task.split(":")[-1] if ":" in task else "default"
        if config_file_name not in presets.get(task_name, {}):
            raise FileNotFoundError(f"No {mode.value} preset for {task_name}:{config_file_name}.")

        module = import_module(f"evaluation.tasks.{mode.value}.{task_name}")
        task_config = dict(presets[task_name][config_file_name])

        task_type = task_config.pop("task_class")

        task_class = getattr(module, task_type)
        # Update with override
        if hparam_overrides is not None:
            task_config["hparams"] = {**task_config["hparams"], **hparam_overrides}
        process_override = {}
        if limit:
            process_override["limit"] = True 
        if flex:
            process_override["flex"] = True
        if task_type == 'WildJailbreakValidationBenign':
            evaluation_tasks.append(task_class(**task_config, **process_override, benign=True))
        else:
            evaluation_tasks.append(task_class(**task_config, **process_override))

    return evaluation_tasks


def wrap_task_with_jailbreak(task: TaskBase, attack: str) -> JailbreakBase:
    """
    Apply the attack to the task.
    Args:
        task: Task to apply the attack.

        attack: Attack to apply.
            similar to task, it can be xxx or xxx:yyy where xxx is the attack name and yyy is the attack config file name.
            if yyy is not provided, it will be assumed as xxx/default.yaml.

    Returns:
        Jailbreak object.
    """
    module = import_module(f"tasks.jailbreaks.{attack}")
    config_file_name = attack.split(":")[-1] if ":" in attack else "default"
    attack_config_file = os.path.join(
        os.path.dirname(__file__), f"{attack.split(':')[0]}/{config_file_name}.yaml"
    )

    with open(attack_config_file, "r") as f:
        attack_config = yaml.safe_load(f)

    attack_class = getattr(module, attack_config.pop("attack_class"))
    jailbreak_task = attack_class(task, **attack_config)
    return jailbreak_task
