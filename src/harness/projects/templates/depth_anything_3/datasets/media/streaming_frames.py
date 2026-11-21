"""Select a lexicographically ordered sequence of local streaming frames."""

from pathlib import Path


def streaming_frames(image_dir):
    source = Path(image_dir)
    if not source.is_dir():
        raise ValueError(f"Streaming frame directory does not exist: {source}")
    frames = sorted(str(path) for path in source.iterdir()
                    if path.is_file() and path.suffix in {".png", ".jpg"})
    if not frames:
        raise ValueError(f"No streaming frames found in {source}")
    return frames
