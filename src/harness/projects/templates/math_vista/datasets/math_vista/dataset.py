"""Load a MathVista split for generation, scoring, or precheck."""

from itertools import islice
from pathlib import Path
from io import BytesIO

from PIL import Image

from datasets import Image as DatasetImage, load_dataset

from mathvista.runtime import data_root
from utilities import read_json


def load_split(source, split, *, images=False, local_file=None, limit=None):
    if local_file:
        path = Path(local_file)
        if not path.is_absolute() and not path.is_file():
            path = data_root() / path
        rows = read_json(path)
        return {str(pid): row for pid, row in islice(rows.items(), limit)}

    data = load_dataset(source, split=split, streaming=limit is not None)
    if not images and "decoded_image" in (data.column_names or []):
        data = data.remove_columns("decoded_image")
    if images and "decoded_image" in (data.column_names or []):
        data = data.cast_column("decoded_image", DatasetImage(decode=False))
    return {str(row["pid"]): row for row in islice(data, limit)}

def open_image(problem):
    image = problem.get("decoded_image")
    if isinstance(image, Image.Image):
        return image
    if isinstance(image, dict) and image.get("bytes"):
        return Image.open(BytesIO(image["bytes"]))
    path = image.get("path") if isinstance(image, dict) else None
    return Image.open(data_root() / (path or problem["image"]))
