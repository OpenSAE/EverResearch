"""Run relative-depth prediction on every frame of a video and write an MP4."""

import cv2
import numpy as np

from ..image_depth.predict import depth_preview


def predict(args, model, files, output_path, *, frame_limit=None):
    for index, source in enumerate(files):
        print(f"Progress {index + 1}/{len(files)}: {source}")
        video = cv2.VideoCapture(str(source))
        try:
            if not video.isOpened():
                raise ValueError(f"Cannot open video: {source}")
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(video.get(cv2.CAP_PROP_FPS))
            output_width = width if args.pred_only else width * 2 + 50
            path = output_path(source, index, "depth_video", ".mp4")
            writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (output_width, height))
            try:
                if not writer.isOpened():
                    raise OSError(f"Cannot write video: {path}")
                spacer = np.full((height, 50, 3), 255, dtype=np.uint8)
                frames = 0
                while frame_limit is None or frames < frame_limit:
                    success, frame = video.read()
                    if not success:
                        break
                    depth = model.infer_image(frame, args.input_size)
                    preview = depth_preview(depth, args.grayscale, "Spectral_r")
                    writer.write(preview if args.pred_only else cv2.hconcat([frame, spacer, preview]))
                    frames += 1
                if frames == 0:
                    raise ValueError(f"Cannot decode a frame from video: {source}")
            finally:
                writer.release()
        finally:
            video.release()
