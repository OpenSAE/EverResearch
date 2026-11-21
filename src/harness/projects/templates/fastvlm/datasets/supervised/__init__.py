"""Read the conversation shards and images used by LLaVA supervised training."""
import json
from pathlib import Path

from PIL import Image


def read_training_rows(data_paths):
    rows = []
    for index, path in enumerate(data_paths):
        with Path(path).open(encoding="utf-8") as source:
            rows.extend({**row, "img_path_idx": index} for row in json.load(source))
    return rows


def read_training_image(image_folders, row):
    index = row["img_path_idx"]
    if image_folders is None or index >= len(image_folders):
        raise ValueError(f"Training data shard {index + 1} requires an --image_folder entry.")
    with Image.open(Path(image_folders[index]) / row["image"]) as image:
        return image.convert("RGB")
