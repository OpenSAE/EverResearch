"""Read one local image as RGB and preserve its identity and original size."""
import hashlib

from PIL import Image


def read_image(path, dataset="user_image"):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        stream.seek(0)
        with Image.open(stream) as source:
            image = source.convert("RGB")

    return image, {
        "dataset": dataset,
        "path": str(path),
        "sha256": digest.hexdigest(),
        "size": list(image.size),
    }
