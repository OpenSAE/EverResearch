"""Read one example per local training or validation file before starting veRL."""

from pathlib import Path
from urllib.parse import urlparse

import yaml


def check_training_inputs(overrides):
    from pyarrow.parquet import ParquetFile

    checks = []
    for split in ("train", "val"):
        key = f"data.{split}_files"
        value = yaml.safe_load(overrides[key])
        paths = value if isinstance(value, list) else [value]
        if not paths or any(not isinstance(path, str) or not path for path in paths):
            raise ValueError(f"{key} must name at least one Parquet file")
        for path in paths:
            if urlparse(path).scheme and not path.startswith("file://"):
                checks.append({"split": split, "path": path, "check": "deferred_to_verl"})
                continue
            filename = Path(urlparse(path).path) if path.startswith("file://") else Path(path)
            with ParquetFile(filename.expanduser()) as source:
                batch = next(source.iter_batches(batch_size=1), None)
                if batch is None:
                    raise ValueError(f"{path} contains no {split} examples")
                row = batch.to_pylist()[0]
                if not row.get("question") or not isinstance(row.get("extra_info"), dict):
                    raise ValueError(f"{path} must contain question text and extra_info metadata")
                checks.append({"split": split, "path": path, "count": source.metadata.num_rows})
    return checks
