# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import os
from pathlib import Path
import torch
import argparse
import numpy as np

from PIL import Image
from cotracker.utils.visualizer import Visualizer, read_video_from_path
from cotracker.predictor import CoTrackerPredictor

from cotracker.hub_api import cotracker3_offline

DEFAULT_DEVICE = (
    "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
)

# if from cotracker.hub_api import cotracker3_offline

DEFAULT_DEVICE == "mps":
#     os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video_path",
        default=str(Path.cwd() / "assets/videos/apple/files/apple.mp4"),
        help="path to a video",
    )
    parser.add_argument(
        "--mask_path",
        default=str(Path.cwd() / "assets/videos/apple/files/apple_mask.png"),
        help="path to a segmentation mask",
    )
    parser.add_argument(
        "--checkpoint",
        # default="./checkpoints/cotracker.pth",
        default=None,
        help="CoTracker model parameters",
    )
    parser.add_argument("--grid_size", type=int, default=10, help="Regular grid size")
    parser.add_argument(
        "--grid_query_frame",
        type=int,
        default=0,
        help="Compute dense and grid tracks starting from this frame",
    )
    parser.add_argument(
        "--backward_tracking",
        action="store_true",
        help="Compute tracks in both directions, not only forward",
    )
    parser.add_argument(
        "--use_v2_model",
        action="store_true",
        help="Pass it if you wish to use CoTracker2, CoTracker++ is the default now",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Pass it if you would like to use the offline model, in case of online don't pass it",
    )

    parser.add_argument("--output-dir", default="./saved_videos")
    args = parser.parse_args()

    # load the input video frame by frame
    video = read_video_from_path(args.video_path)
    video = torch.from_numpy(video).permute(0, 3, 1, 2)[None].float()
    segm_mask = np.array(Image.open(os.path.join(args.mask_path)))
    segm_mask = torch.from_numpy(segm_mask)[None, None]

    if args.checkpoint is not None:
        if args.use_v2_model:
            model = CoTrackerPredictor(checkpoint=args.checkpoint, v2=args.use_v2_model)
        else:
            if args.offline:
                window_len = 60
            else:
                window_len = 16
            model = CoTrackerPredictor(
                checkpoint=args.checkpoint,
                v2=args.use_v2_model,
                offline=args.offline,
                window_len=window_len,
            )
    else:
        model = cotracker3_offline()

    model = model.to(DEFAULT_DEVICE)
    video = video.to(DEFAULT_DEVICE)

    pred_tracks, pred_visibility = model(
        video,
        grid_size=args.grid_size,
        grid_query_frame=args.grid_query_frame,
        backward_tracking=args.backward_tracking,
        # segm_mask=segm_mask
    )
    print("computed")

    # save a video with predicted tracks
    seq_name = args.video_path.split("/")[-1]
    vis = Visualizer(save_dir=args.output_dir, pad_value=120, linewidth=3)
    vis.visualize(
        video,
        pred_tracks,
        pred_visibility,
        query_frame=0 if args.backward_tracking else args.grid_query_frame,
    )


if __name__ == "__main__":
    main()
