"""Check an image prediction's input, prompt, and device without writing results."""
from argparse import ArgumentParser
from pathlib import Path

from .gate import check_image


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--point", required=True, nargs=2, type=float)
    args = parser.parse_args()
    try:
        _, image, device = check_image({
            "image": args.image,
            "checkpoint": args.checkpoint,
            "device": args.device,
            "points": [(*args.point, 1)],
        })
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"{image.width} × {image.height} RGB image is ready on {device}")
