"""Command-line entry point for exporting VGGT predictions to COLMAP."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "base"))
import geometry_runtime

from vggt.demos.colmap import demo_fn, main, parse_args, rename_colmap_recons_and_rescale_camera, run_VGGT


if __name__ == "__main__":
    main()
