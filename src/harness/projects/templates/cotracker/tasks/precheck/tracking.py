"""Check point tracking on a few real frames before publishing a formal result."""

from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from cotracker.datasets.video import read_video_from_path
from cotracker.tracking.points import track_points, write_overlay


def precheck_tracking(model, frames, device, configuration):
    start = monotonic()
    requested_frame = configuration["grid_query_frame"]
    if not 0 <= requested_frame < len(frames):
        raise ValueError(f"Query frame {requested_frame} is outside the decoded video")
    if configuration["grid_size"] < 1:
        raise ValueError("Grid size must be positive for a managed tracking run")
    backward = configuration["backward_tracking"]
    first_frame = max(requested_frame - 1, 0) if backward else requested_frame
    sample = frames[first_frame:first_frame + 4]
    grid = min(configuration["grid_size"], 2)
    result = track_points(model, sample, device, grid, requested_frame - first_frame, backward)
    _, tracks, visibility = result
    points = grid ** 2
    if tracks.shape != (1, len(sample), points, 2) or visibility.shape != (1, len(sample), points):
        raise ValueError("The model returned unexpected track or visibility dimensions")
    with TemporaryDirectory(prefix="cotracker-precheck-") as directory:
        overlay = write_overlay(Path(directory), *result, query_frame=0)
        if read_video_from_path(overlay) is None:
            raise ValueError("The point tracking preview could not be decoded")
    return {
        "status": "passed",
        "samples_checked": len(sample),
        "steps": 1,
        "wall_seconds": monotonic() - start,
        "track_shape": list(tracks.shape),
    }
