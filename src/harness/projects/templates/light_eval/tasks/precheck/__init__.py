"""Check representative evaluation samples before entering model or baseline execution."""

from collections.abc import Mapping, Sequence

from lighteval.tasks.requests import Doc, SamplingMethod


def check_samples(documents: Mapping[str, Sequence[Doc]], *, asynchronous_model: bool = False) -> int:
    """Check one loaded sample for each task and required sampling method."""
    if not documents:
        raise ValueError("Select at least one evaluation task.")
    for task, docs in documents.items():
        if not docs:
            raise ValueError(f"Task {task!r} has no evaluation samples in the selected input.")
        sample = docs[0]
        if not isinstance(sample.query, str):
            raise ValueError(f"Task {task!r} must provide a text prompt.")
        if SamplingMethod.LOGPROBS in sample.sampling_methods and not sample.choices:
            raise ValueError(f"Task {task!r} requires at least one answer choice for log-probability scoring.")
        if asynchronous_model and SamplingMethod.PERPLEXITY in sample.sampling_methods:
            raise ValueError(f"Task {task!r} requires perplexity scoring, which this asynchronous backend lacks.")
    return len(documents)


def check_inspect_tasks(tasks) -> int:
    """Confirm each Inspect task has an evaluation sample before model dispatch."""
    if not tasks:
        raise ValueError("Select at least one evaluation task.")
    for task in tasks:
        if not len(task.dataset):
            raise ValueError(f"Task {task.name!r} has no evaluation samples in the selected input.")
    return len(tasks)
