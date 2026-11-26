from ai2_safety_datasets.readers.benchmark_files import benchmark_file

import os

from evaluation.tasks.generation.base import AdversarialTaskBase
from src.data_utils import load_standard_data


class DoAnythingNow(AdversarialTaskBase):
    def load(self) -> list[dict]:
        task_file = benchmark_file("generation", "do_anything_now", "do_anything_now_jailbreak.jsonl")
        data = load_standard_data(task_file)
        for item in data:
            item["instruction"] = item["adversarial"]
        if self.limit:
            return data[:5]
        return data
