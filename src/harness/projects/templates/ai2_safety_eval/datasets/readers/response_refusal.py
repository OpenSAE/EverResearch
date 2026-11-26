"""Read XSTest's labeled response-refusal split."""

from datasets import load_dataset

from src.classifier_models.base import ResponseRefusal


def load_xstest_response_refusal():
    dataset = load_dataset("allenai/xstest-response", split="response_refusal")
    return [{
        "prompt": row["prompt"],
        "response": row["response"],
        "response_refusal": ResponseRefusal(row["label"]),
        "prompt_type": row["prompt_type"],
        "prompt_harm_category": row["prompt_harm_category"],
    } for row in dataset]
