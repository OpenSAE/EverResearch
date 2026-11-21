"""Command-line entry point for the VGGT Viser viewer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "base"))
import geometry_runtime

from vggt.demos.viser_app import apply_sky_segmentation, main, parser, viser_wrapper


if __name__ == "__main__":
    main()
