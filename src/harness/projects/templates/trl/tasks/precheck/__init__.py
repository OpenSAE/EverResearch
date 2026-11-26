"""Run a bounded forward pass before the maintained training recipe.

The gate uses the prepared batch and loss function from the selected trainer.
"""

import math
from copy import deepcopy

import torch


def check_supervised_batch(trainer):
    """Check real tokenized samples and the loss without updating weights."""
    model = trainer.model
    original_mode = model.training
    original_evaluation_metrics = deepcopy(trainer._metrics["eval"])
    cuda_devices = [model.device] if model.device.type == "cuda" else []
    model.eval()
    try:
        with torch.random.fork_rng(devices=cuda_devices), torch.inference_mode():
            batch = next(iter(trainer.get_train_dataloader()), None)
            if batch is None:
                raise ValueError("The selected training split yielded no batches.")
            loss = float(trainer.compute_loss(model, batch).item())
    finally:
        model.train(original_mode)
        trainer._metrics["eval"] = original_evaluation_metrics
    if not math.isfinite(loss):
        raise ValueError(f"Training precheck produced a nonfinite loss ({loss}).")
    return {"samples_checked": int(batch["input_ids"].size(0)), "loss": loss}
