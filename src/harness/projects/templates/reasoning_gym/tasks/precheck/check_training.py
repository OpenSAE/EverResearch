"""Check representative training and validation rows through real policy generation."""

from math import isfinite

from reasoning_gym.utils import extract_answer


def check_policy(model, tokenizer, train_dataset, validation_dataset):
    import torch

    report = {"samples_checked": 2, "splits": {}}
    model.eval()
    try:
        for name, dataset in (("train", train_dataset), ("validation", validation_dataset)):
            sample = dataset[0]
            inputs = tokenizer(sample["prompt"], return_tensors="pt", add_special_tokens=False).to(model.device)
            if inputs["input_ids"].numel() == 0:
                raise ValueError(f"The {name} prompt produced no tokens")
            with torch.inference_mode():
                result = model.generate(**inputs, max_new_tokens=8, do_sample=False)
            completion = result[0, inputs["input_ids"].shape[1]:]
            if completion.numel() == 0:
                raise ValueError(f"The model produced no continuation for the {name} prompt")
            response = tokenizer.decode(completion, skip_special_tokens=True)
            reward = dataset.data.score_answer(extract_answer(response), sample["item"])
            if not isfinite(reward):
                raise ValueError(f"The {name} reward is not finite")
            report["splits"][name] = {"completion_tokens": completion.numel(), "reward": reward}
    finally:
        model.train()
    return report
