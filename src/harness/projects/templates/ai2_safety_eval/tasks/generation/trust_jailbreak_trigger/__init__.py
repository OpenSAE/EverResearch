from ai2_safety_datasets.readers.benchmark_files import benchmark_file

import os

from evaluation.tasks.generation.base import AdversarialTaskBase
from src.data_utils import load_standard_data


class TrustLLMJailbreakTriggerSubset(AdversarialTaskBase):
    def load(self) -> list[dict]:
        task_file = benchmark_file("generation", "trustllm_jailbreaktrigger", "trustllm_jailbreaktrigger_400.jsonl")
        data = load_standard_data(task_file)
        for item in data:
            item["instruction"] = item["prompt"]
        if self.limit:
            return data[:5]
        return data
