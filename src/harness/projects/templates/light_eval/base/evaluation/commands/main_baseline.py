# MIT License

# Copyright (c) 2024 The HuggingFace Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from lighteval.cli_args import (
    custom_tasks,
    dataset_loading_processes,
    experiment_name,
    load_tasks_multilingual,
    max_samples,
    output_dir,
    tasks,
)


def baseline(
    tasks: tasks.type,
    load_tasks_multilingual: load_tasks_multilingual.type = load_tasks_multilingual.default,
    dataset_loading_processes: dataset_loading_processes.type = dataset_loading_processes.default,
    custom_tasks: custom_tasks.type = custom_tasks.default,
    output_dir: output_dir.type = output_dir.default,
    max_samples: max_samples.type = max_samples.default,
    experiment_name: experiment_name.type = experiment_name.default,
):
    """Compute baselines for given tasks.

    It has been tested with generative and accuracy tasks, but may not work correctly for other task types.

    The baseline is computed as follows:

    - For multiple-choice tasks: It assumes random guessing, so the score is n_correct/number_of_choices.
    - For other metrics: It assigns a score of 0, which may not be appropriate for all task types.

    Note:
        This baseline computation may not be suitable for all task types and should be used with caution.
    """
    from lighteval.chance_baseline import score_sample
    from lighteval.logging.evaluation_tracker import EvaluationTracker
    from lighteval.precheck import check_samples
    from lighteval.tasks.lighteval_task import LightevalTask
    from lighteval.tasks.registry import Registry

    registry = Registry(tasks=tasks, custom_tasks=custom_tasks, load_multilingual=load_tasks_multilingual)
    tasks_dict: dict[str, LightevalTask] = registry.load_tasks()

    evaluation_tracker = EvaluationTracker(
        output_dir=output_dir,
        experiment_name=experiment_name,
        save_details=False,
        push_to_hub=False,
        push_to_tensorboard=False,
        public=False,
        hub_results_org=None,
    )
    evaluation_tracker.set_experiment_location(
        datasets=[str(task.dataset_path) for task in tasks_dict.values()],
        models=[],
        tasks=[task.full_name for task in tasks_dict.values()],
    )
    evaluation_tracker.general_config_logger.model_name = "baseline"
    evaluation_tracker.general_config_logger.log_args_info(num_fewshot_seeds=0, max_samples=max_samples, job_id="")

    LightevalTask.load_datasets(tasks_dict, dataset_loading_processes)
    evaluation_tracker.task_config_logger.log(tasks_dict)

    docs_by_task = {name: task.get_docs(max_samples) for name, task in tasks_dict.items()}
    check_samples(docs_by_task)
    for task_name, task in tasks_dict.items():
        docs = docs_by_task[task_name]
        for task_doc in docs:
            evaluation_tracker.metrics_logger.log(task_name, score_sample(task, task_doc))
        evaluation_tracker.task_config_logger.log_num_docs(task_name, len(task.eval_docs()), len(docs))
        evaluation_tracker.versions_logger.log(task_name, task.version)

    evaluation_tracker.metrics_logger.aggregate(task_dict=tasks_dict, bootstrap_iters=1000)
    evaluation_tracker.general_config_logger.log_end_time()
    evaluation_tracker.save()
