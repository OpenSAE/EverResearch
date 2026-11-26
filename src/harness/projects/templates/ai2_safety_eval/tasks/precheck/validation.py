"""Verify a selected evaluation model and task on a bounded set of real samples."""

from time import perf_counter


def select_samples(task, limit):
    if limit is not None:
        if limit < 1:
            raise ValueError("The sample limit must be at least one.")
        task.data = task.data[:limit]


def check_selection(task, model):
    task.validate_if_model_is_compatible(model)
    if not task.data:
        raise ValueError(f"{type(task).__name__} has no samples.")


def check_evaluation(task, model, limit):
    workload = len(task.data)
    sample_count = min(workload, limit)
    if sample_count < workload:
        task.data = [
            task.data[(2 * index + 1) * workload // (2 * sample_count)]
            for index in range(sample_count)
        ]

    check_selection(task, model)
    started = perf_counter()
    metrics, results = task.evaluate(model)
    elapsed = perf_counter() - started
    if not metrics or not results:
        raise ValueError(f"{type(task).__name__} returned no metrics or sample results.")
    result_sets = results if isinstance(results[0], list) else [results]
    if any(len(result_set) != sample_count for result_set in result_sets):
        raise ValueError(f"{type(task).__name__} returned a different number of predictions than samples.")

    parsing_error_rate = metrics.get("parsing_error")
    parsing_errors = metrics.get("error_metrics", {}).get("parsing_errors")
    if parsing_errors is not None:
        parsing_error_rate = parsing_errors / sample_count
    return {
        "samples": sample_count,
        "full_sample_count": workload,
        "batch_size": getattr(model, "batch_size", None),
        "evaluation_seconds": elapsed,
        "model_load_seconds": getattr(model, "model_load_seconds", None),
        "parsing_error_rate": parsing_error_rate,
        "metrics": sorted(metrics),
    }
