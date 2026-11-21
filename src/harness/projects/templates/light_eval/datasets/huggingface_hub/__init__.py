"""Load Hugging Face Hub evaluation datasets and resolve their few-shot splits."""

from collections.abc import Callable, Mapping, Sequence

from datasets import DatasetDict, load_dataset


def load_hub_dataset(
    path: str,
    name: str,
    *,
    revision: str | None,
    data_files: str | Sequence[str] | Mapping[str, str | Sequence[str]] | None,
    row_filter: Callable[[dict], bool] | None,
) -> DatasetDict:
    """Load all splits for the selection and apply its optional row filter."""
    dataset = load_dataset(path=path, name=name, revision=revision, data_files=data_files)
    if row_filter is not None:
        dataset = dataset.filter(row_filter)
    return dataset  # type: ignore[return-value]


def infer_fewshot_split(available_splits: Sequence[str], evaluation_splits: Sequence[str]) -> str | None:
    """Find the first training or validation split outside the evaluation splits."""
    return next(
        (
            split
            for preferred in ("train", "dev", "valid", "default")
            for split in available_splits
            if preferred in split and split not in evaluation_splits
        ),
        None,
    )
