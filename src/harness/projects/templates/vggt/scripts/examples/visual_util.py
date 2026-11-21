"""Compatibility imports for VGGT demonstration visualization helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "base"))
import geometry_runtime

from vggt.demos.visualization import (
    apply_scene_alignment,
    compute_camera_faces,
    download_file_from_url,
    get_opengl_conversion_matrix,
    integrate_camera_into_scene,
    predictions_to_glb,
    run_skyseg,
    segment_sky,
    transform_points,
)
