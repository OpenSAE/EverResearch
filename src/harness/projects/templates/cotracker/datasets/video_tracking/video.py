"""Decode videos for CoTracker demos and programmatic point tracking.

The legacy visualizer import also exposes this reader for existing callers.
"""

import imageio
import numpy as np


def read_video_from_path(path):
    try:
        with imageio.get_reader(path) as reader:
            return np.stack([np.asarray(frame) for frame in reader])
    except (OSError, ValueError, RuntimeError) as error:
        print("Error opening video file: ", error)
        return None
