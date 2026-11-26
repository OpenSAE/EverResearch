"""Validate the actual configured datasets with a bounded scoring pass.

Remote and local evaluation call this gate before using their model adapters.
"""

from math import isfinite


def check_datasets(categories, build_dataset):
    checked = []
    for category in categories:
        for dataset_config in category.datasets:
            dataset = build_dataset(dataset_config)
            entry = dataset[0]
            if not isinstance(entry["question"], str) or not entry["question"]:
                raise ValueError(f"{dataset_config.dataset} returned an empty or invalid question")
            score = dataset.score_answer(answer=entry["answer"], entry=entry)
            if not isfinite(score):
                raise ValueError(f"{dataset_config.dataset} returned a non-finite score")
            checked.append({"dataset": dataset_config.dataset, "reference_score": score})
    if not checked:
        raise ValueError("The selected configuration contains no datasets")
    return checked
