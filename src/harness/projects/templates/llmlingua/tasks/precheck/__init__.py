"""Check selected input and model contracts before starting full tasks."""

from itertools import chain


def preview_compression(results):
    """Return a checked first result and replay it in the full results stream."""
    first = next(results, None)
    if first is None:
        return None, iter(())
    return first, chain((first,), results)


def check_training_splits(training, validation):
    """Check that both splits have a tokenizable sample before training."""
    if not len(training) or not len(validation):
        raise ValueError(
            "Classifier training requires nonempty training and validation splits."
        )
    validation[0]
    return training[0]


def check_training_sample(model, sample, device):
    """Run a single labeled model forward with no gradient tracking."""
    import torch

    with torch.no_grad():
        return model(
            input_ids=sample["ids"].unsqueeze(0).to(device),
            attention_mask=sample["mask"].unsqueeze(0).to(device),
            labels=sample["targets"].unsqueeze(0).to(device),
        )


def check_evaluation_rows(rows, path, required_fields):
    """Validate one benchmark input row before model calls or output writes."""
    try:
        sample = next((row for row in rows if not isinstance(row, float)), None)
    except TypeError as exc:
        raise ValueError(f"{path}: expected a JSON collection.") from exc
    if not isinstance(sample, dict):
        raise ValueError(
            f"{path}: expected a JSON collection with at least one sample object."
        )
    missing = [field for field in required_fields if field not in sample]
    if missing:
        raise ValueError(f"{path}: first sample is missing {', '.join(missing)}.")
