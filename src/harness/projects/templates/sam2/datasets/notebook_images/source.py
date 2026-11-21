"""Load the RGB images accepted by the point-prompt task."""
from PIL import Image


def open_rgb(path):
    with Image.open(path) as source:
        return source.convert("RGB")
