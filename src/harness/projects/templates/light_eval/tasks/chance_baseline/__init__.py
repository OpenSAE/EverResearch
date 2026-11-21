"""Estimate baseline metrics for a sample under uniform guessing."""

from lighteval.tasks.lighteval_task import LightevalTask
from lighteval.tasks.requests import Doc, SamplingMethod
from lighteval.utils.utils import as_list


def score_sample(task: LightevalTask, doc: Doc) -> dict[str, float]:
    """Assign the chance rate to multiple-choice metrics and zero to other metrics."""
    return {
        metric_name: len(as_list(doc.gold_index)) / len(doc.choices)
        if metric.category == SamplingMethod.LOGPROBS
        else 0
        for metric in task.metrics
        for metric_name in metric.get_corpus_aggregations()
    }
