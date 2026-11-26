"""Run relative or metric depth prediction and write the original visualization formats."""

import cv2
import matplotlib
import numpy as np


def depth_preview(depth, grayscale, palette):
    if not np.isfinite(depth).all():
        raise ValueError("The depth model returned non-finite values.")
    low, high = depth.min(), depth.max()
    scaled = ((depth - low) / (high - low) * 255.0).astype(np.uint8) if high > low else np.zeros(depth.shape, np.uint8)
    if grayscale:
        return np.repeat(scaled[..., np.newaxis], 3, axis=-1)
    cmap = matplotlib.colormaps.get_cmap(palette)
    return (cmap(scaled)[:, :, :3] * 255)[:, :, ::-1].astype(np.uint8)


def predict(args, model, files, output_path):
    palette = "Spectral" if args.command == "metric" else "Spectral_r"
    for index, source in enumerate(files):
        print(f"Progress {index + 1}/{len(files)}: {source}")
        image = cv2.imread(str(source))
        if image is None:
            raise ValueError(f"Cannot read image: {source}")
        depth = model.infer_image(image, args.input_size)
        if getattr(args, "save_numpy", False):
            np.save(output_path(source, index, "raw_depth_meter", ".npy"), depth)
        preview = depth_preview(depth, args.grayscale, palette)
        if not args.pred_only:
            spacer = np.full((image.shape[0], 50, 3), 255, np.uint8)
            preview = cv2.hconcat([image, spacer, preview])
        if not cv2.imwrite(str(output_path(source, index, "depth_map", ".png")), preview):
            raise OSError(f"Cannot write prediction for {source}")
