"""Track a grid of points in a decoded video and write upstream-style overlays."""

import torch
from cotracker.utils.visualizer import Visualizer


def select_device(name):
    if name != "auto":
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def track_points(model, frames, device, grid_size, query_frame, backward_tracking):
    video = torch.from_numpy(frames).permute(0, 3, 1, 2)[None].float().to(device)
    tracks, visibility = model(
        video,
        grid_size=grid_size,
        grid_query_frame=query_frame,
        backward_tracking=backward_tracking,
    )
    return video, tracks, visibility


def write_overlay(directory, video, tracks, visibility, query_frame):
    Visualizer(save_dir=str(directory), pad_value=120, linewidth=3).visualize(
        video,
        tracks,
        visibility,
        filename="video",
        query_frame=query_frame,
    )
    return directory / "video.mp4"
