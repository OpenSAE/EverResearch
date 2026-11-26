from ai2_safety_datasets.readers.benchmark_files import benchmark_file

import os

from src.data_utils import load_standard_data
from evaluation.tasks.generation.base import AdversarialTaskBase


class WildJailbreakValidation(AdversarialTaskBase):
    def load(self) -> list[dict]:
        task_file = benchmark_file("generation", "wildjailbreak", "harmful.jsonl")
        data = load_standard_data(task_file)
        for item in data:
            item["instruction"] = item["adversarial"]
        if self.limit:
            return data[:5]
        return data


class WildJailbreakValidationBenign(AdversarialTaskBase):
    def load(self) -> list[dict]:
        task_file = benchmark_file("generation", "wildjailbreak", "benign.jsonl")
        data = load_standard_data(task_file)
        for item in data:
            item["instruction"] = item["adversarial"]
            # Delete 'vanilla' field, so we use the 'instruction' field for classifier judge input
            del item["vanilla"]
        if self.limit:
            return data[:5]
        return data
