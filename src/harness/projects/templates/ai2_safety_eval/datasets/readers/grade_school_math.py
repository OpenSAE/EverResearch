"""Read the upstream GSM8K test split."""

import json

from .downloads import download_benchmark_file


def load_test_rows():
    path = download_benchmark_file(
        "gsm8k", "test.jsonl",
        "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl",
    )
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]
