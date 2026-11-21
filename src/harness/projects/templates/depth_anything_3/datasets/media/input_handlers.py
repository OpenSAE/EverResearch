# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Input Processing Service
Handles different types of inputs (image, images, colmap, video)
"""

import math
import os
from typing import List, Optional, Tuple
import cv2
import numpy as np
import typer

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}


class InputHandler:
    """Base input handler class"""

    @staticmethod
    def validate_path(path: str, path_type: str = "file") -> str:
        """Validate path"""
        if not os.path.exists(path):
            raise typer.BadParameter(f"{path_type} not found: {path}")
        return path

    @staticmethod
    def handle_export_dir(export_dir: str, auto_cleanup: bool = False) -> str:
        """Handle export directory"""
        if os.path.exists(export_dir):
            if auto_cleanup:
                typer.echo(f"Auto-cleaning existing export directory: {export_dir}")
                import shutil

                shutil.rmtree(export_dir)
                os.makedirs(export_dir, exist_ok=True)
            else:
                typer.echo(f"Export directory '{export_dir}' already exists.")
                if typer.confirm("Do you want to clean it and continue?"):
                    import shutil

                    shutil.rmtree(export_dir)
                    os.makedirs(export_dir, exist_ok=True)
                    typer.echo(f"Cleaned export directory: {export_dir}")
                else:
                    typer.echo("Operation cancelled.")
                    raise typer.Exit(0)
        else:
            os.makedirs(export_dir, exist_ok=True)
        return export_dir


class ImageHandler(InputHandler):
    """Single image handler"""

    @staticmethod
    def process(image_path: str) -> List[str]:
        """Process single image"""
        InputHandler.validate_path(image_path, "Image file")
        return [image_path]


class ImagesHandler(InputHandler):
    """Image directory handler"""

    @staticmethod
    def process(images_dir: str, image_extensions: str = "png,jpg,jpeg") -> List[str]:
        """Process image directory"""
        if not os.path.isdir(images_dir):
            raise typer.BadParameter(f"Images directory not found: {images_dir}")

        # Parse extensions
        extensions = [ext.strip().lower() for ext in image_extensions.split(",")]
        extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

        with os.scandir(images_dir) as entries:
            image_files = sorted(
                entry.path for entry in entries
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in extensions
            )

        if not image_files:
            raise typer.BadParameter(
                f"No image files found in {images_dir} with extensions: {extensions}"
            )

        typer.echo(f"Found {len(image_files)} images to process")
        return image_files


class ColmapHandler(InputHandler):
    """COLMAP data handler"""

    @staticmethod
    def process(
        colmap_dir: str, sparse_subdir: str = ""
    ) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """Process COLMAP data"""
        InputHandler.validate_path(colmap_dir, "COLMAP directory")

        # Build paths
        images_dir = os.path.join(colmap_dir, "images")
        if sparse_subdir:
            sparse_dir = os.path.join(colmap_dir, "sparse", sparse_subdir)
        else:
            sparse_dir = os.path.join(colmap_dir, "sparse")

        if not os.path.isdir(images_dir):
            raise typer.BadParameter(f"Images directory not found: {images_dir}")
        InputHandler.validate_path(sparse_dir, "Sparse reconstruction directory")

        from ..utils.read_write_model import read_model

        # Load COLMAP data
        typer.echo("Loading COLMAP reconstruction data...")
        try:
            cameras, images, points3D = read_model(sparse_dir)

            typer.echo(
                f"Loaded COLMAP data: {len(cameras)} cameras, {len(images)} images, "
                f"{len(points3D)} 3D points."
            )

            # Get image files and pose data
            image_files = []
            extrinsics = []
            intrinsics = []

            for image_id, image_data in images.items():
                image_name = image_data.name
                image_path = os.path.join(images_dir, image_name)

                if os.path.exists(image_path):
                    image_files.append(image_path)

                    # Get camera parameters
                    camera = cameras[image_data.camera_id]

                    # Convert quaternion to rotation matrix
                    R = image_data.qvec2rotmat()
                    t = image_data.tvec

                    # Create extrinsic matrix (world to camera)
                    extrinsic = np.eye(4)
                    extrinsic[:3, :3] = R
                    extrinsic[:3, 3] = t
                    extrinsics.append(extrinsic)

                    # Create intrinsic matrix
                    if camera.model == "PINHOLE":
                        fx, fy, cx, cy = camera.params
                    elif camera.model == "SIMPLE_PINHOLE":
                        f, cx, cy = camera.params
                        fx = fy = f
                    else:
                        # For other models, use basic pinhole approximation
                        fx = fy = camera.params[0] if len(camera.params) > 0 else 1000
                        cx = camera.width / 2
                        cy = camera.height / 2

                    intrinsic = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
                    intrinsics.append(intrinsic)

            if not image_files:
                raise typer.BadParameter("No valid images found in COLMAP data")

            typer.echo(f"Found {len(image_files)} valid images with pose data")

            return image_files, np.array(extrinsics), np.array(intrinsics)

        except Exception as e:
            raise typer.BadParameter(f"Failed to load COLMAP data: {e}")


class VideoHandler(InputHandler):
    """Video handler"""

    @staticmethod
    def process(
        video_path: str, output_dir: str, fps: float = 1.0, max_frames: Optional[int] = None
    ) -> List[str]:
        """Process video, extract frames"""
        InputHandler.validate_path(video_path, "Video file")

        validate_sampling_fps(fps)
        cap = cv2.VideoCapture(video_path)
        try:
            if not cap.isOpened():
                raise typer.BadParameter(f"Cannot open video: {video_path}")
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            if not math.isfinite(video_fps) or video_fps <= 0:
                raise typer.BadParameter(f"Video FPS is unavailable: {video_path}")

            frame_ratio = video_fps / fps
            if not math.isfinite(frame_ratio):
                raise typer.BadParameter("Sampling FPS is too low for this video.", param_hint="--fps")
            frame_interval = max(1, int(frame_ratio))
            actual_fps = video_fps / frame_interval
            typer.echo(f"Extracting frames at {actual_fps:.2f} FPS (every {frame_interval} frame(s))")

            frames_dir = os.path.join(output_dir, "input_images")
            os.makedirs(frames_dir, exist_ok=True)
            frame_files = []
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % frame_interval == 0:
                    frame_path = os.path.join(frames_dir, f"{len(frame_files):06d}.png")
                    if not cv2.imwrite(frame_path, frame):
                        raise typer.BadParameter(f"Cannot write extracted frame: {frame_path}")
                    frame_files.append(frame_path)
                    if max_frames is not None and len(frame_files) >= max_frames:
                        break
                frame_count += 1
        finally:
            cap.release()

        if not frame_files:
            raise typer.BadParameter("No frames extracted from video")
        typer.echo(f"Extracted {len(frame_files)} frames to {frames_dir}")
        return frame_files


def validate_sampling_fps(fps: float) -> None:
    """Reject invalid frame sampling rates before creating output directories."""
    if not math.isfinite(fps) or fps <= 0:
        raise typer.BadParameter("Sampling FPS must be a finite positive number.", param_hint="--fps")


def parse_export_feat(export_feat_str: str) -> List[int]:
    """Parse export_feat parameter"""
    if not export_feat_str:
        return []

    try:
        return [int(x.strip()) for x in export_feat_str.split(",") if x.strip()]
    except ValueError:
        raise typer.BadParameter(
            f"Invalid export_feat format: {export_feat_str}. "
            "Use comma-separated integers like '0,1,2'"
        )
