# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import glob
import json
import os
import random
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from vggt.precheck.gate import check_images
from vggt.runtime_paths import execution_id, experiment_root, run_name
from vggt.utils.geometry import unproject_depth_map_to_point_map
from vggt.utils.helper import create_pixel_coordinate_grid, randomly_limit_trues
from vggt.scene_data.images import load_and_preprocess_images_square
from vggt.utils.pose_enc import pose_encoding_to_extri_intri

from vggt.models.demo_inference import cuda_dtype, load_demo_model
from .records import pack_reconstruction


# TODO: add support for masks
# TODO: add iterative BA
# TODO: add support for radial distortion, which needs extra_params
# TODO: test with more cases
# TODO: test different camera types


def parse_args():
    parser = argparse.ArgumentParser(description="VGGT Demo")
    parser.add_argument("--scene_dir", type=str, required=True, help="Directory containing the scene images")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--output-dir", help="Write COLMAP files directly to this directory")
    output.add_argument("--legacy-layout", action="store_true", help="Write COLMAP files to SCENE_DIR/sparse")
    parser.add_argument("--run-name", help="Name describing the purpose of the reconstruction")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--use_ba", action="store_true", default=False, help="Use BA for reconstruction")
    ######### BA parameters #########
    parser.add_argument(
        "--max_reproj_error", type=float, default=8.0, help="Maximum reprojection error for reconstruction"
    )
    parser.add_argument("--shared_camera", action="store_true", default=False, help="Use shared camera for all images")
    parser.add_argument("--camera_type", type=str, default="SIMPLE_PINHOLE", help="Camera type for reconstruction")
    parser.add_argument("--vis_thresh", type=float, default=0.2, help="Visibility threshold for tracks")
    parser.add_argument("--query_frame_num", type=int, default=8, help="Number of frames to query")
    parser.add_argument("--max_query_pts", type=int, default=4096, help="Maximum number of query points")
    parser.add_argument(
        "--fine_tracking", action="store_true", default=True, help="Use fine tracking (slower but more accurate)"
    )
    parser.add_argument(
        "--conf_thres_value", type=float, default=5.0, help="Confidence threshold value for depth filtering (wo BA)"
    )
    args = parser.parse_args()
    if args.run_name is not None:
        try:
            run_name(args.run_name)
        except ValueError as error:
            parser.error(str(error))
    return args


def save_reconstruction(args, reconstruction, point_cloud, image_names):
    """Write the existing COLMAP payload and record the generated path."""
    scene = Path(args.scene_dir).resolve()
    output_dir = getattr(args, "output_dir", None)
    if output_dir is not None or getattr(args, "legacy_layout", True):
        sparse = Path(output_dir).absolute() if output_dir is not None else scene / "sparse"
        sparse.mkdir(parents=True, exist_ok=True)
        reconstruction.write(str(sparse))
        point_cloud.export(str(sparse / "points.ply"))
        print(f"Saved reconstruction to {sparse}")
        return sparse

    dataset = scene.name if scene.name == "llff_fern" else "scene_images"
    subname = run_name(getattr(args, "run_name", None) or ("bundle_adjustment" if args.use_ba else "feed_forward"))
    run_id = execution_id(datetime.now(timezone.utc))
    run = experiment_root() / dataset / "geometry_transformer" / "reconstruction" / subname / "executions" / run_id
    metadata = run / "metadata"
    metadata.mkdir(parents=True)
    effective = {
        "dataset": dataset,
        "model": "geometry_transformer",
        "task": "reconstruction",
        "input": str(scene / "images"),
        "images": image_names,
        "arguments": vars(args),
    }
    config = metadata / "config.json"
    config.write_text(json.dumps(effective, indent=2) + "\n")
    manifest = metadata / "manifest.json"
    record = {
        "run_id": run_id,
        "subname": subname,
        "task": "reconstruction",
        "effective_config": "metadata/config.json",
        "status": "running",
        "outputs": {},
    }
    bundle = run / "artifacts" / "reconstruction.zip"
    bundle.parent.mkdir()
    temporary = manifest.with_suffix(".tmp")

    def publish():
        temporary.write_text(json.dumps(record, indent=2) + "\n")
        temporary.replace(manifest)

    publish()
    try:
        with tempfile.TemporaryDirectory(dir=run) as directory:
            sparse = Path(directory)
            reconstruction.write(str(sparse))
            point_cloud.export(str(sparse / "points.ply"))
            # The archive's destination must stay outside the directory being copied.
            package = sparse.parent / ".reconstruction.zip"
            pack_reconstruction(sparse, package)
            package.replace(bundle)
    except BaseException as error:
        if "package" in locals():
            package.unlink(missing_ok=True)
        record["status"] = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        publish()
        raise
    record["status"] = "succeeded"
    record["outputs"]["reconstruction"] = "artifacts/reconstruction.zip"
    publish()
    print(f"Run manifest: {manifest}")
    print(f"Saved reconstruction to {bundle}")
    return bundle


def run_VGGT(model, images, dtype, resolution=518):
    # images: [B, 3, H, W]

    assert len(images.shape) == 4
    assert images.shape[1] == 3

    # hard-coded to use 518 for VGGT
    images = F.interpolate(images, size=(resolution, resolution), mode="bilinear", align_corners=False)

    with torch.no_grad():
        with torch.autocast("cuda", dtype=dtype, enabled=dtype is not None):
            images = images[None]  # add batch dimension
            aggregated_tokens_list, ps_idx = model.aggregator(images)

        # Predict Cameras
        pose_enc = model.camera_head(aggregated_tokens_list)[-1]
        # Extrinsic and intrinsic matrices, following OpenCV convention (camera from world)
        extrinsic, intrinsic = pose_encoding_to_extri_intri(pose_enc, images.shape[-2:])
        # Predict Depth Maps
        depth_map, depth_conf = model.depth_head(aggregated_tokens_list, images, ps_idx)

    extrinsic = extrinsic.squeeze(0).cpu().numpy()
    intrinsic = intrinsic.squeeze(0).cpu().numpy()
    depth_map = depth_map.squeeze(0).cpu().numpy()
    depth_conf = depth_conf.squeeze(0).cpu().numpy()
    return extrinsic, intrinsic, depth_map, depth_conf


def demo_fn(args):
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False

    # Print configuration
    print("Arguments:", vars(args))

    # Set seed for reproducibility
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(args.seed)
        torch.cuda.manual_seed_all(args.seed)  # for multi-GPU
    print(f"Setting seed as: {args.seed}")

    # Set device and dtype
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = cuda_dtype(device)
    print(f"Using device: {device}")
    print(f"Using dtype: {dtype}")

    # Get image paths and preprocess them
    image_dir = os.path.join(args.scene_dir, "images")
    image_path_list = sorted(glob.glob(os.path.join(image_dir, "*")))
    if len(image_path_list) == 0:
        raise ValueError(f"No images found in {image_dir}")
    check_images(image_path_list, shared_camera=args.use_ba and args.shared_camera)
    base_image_path_list = [os.path.basename(path) for path in image_path_list]

    # Load images and original coordinates
    # Load Image in 1024, while running VGGT with 518
    vggt_fixed_resolution = 518
    img_load_resolution = 1024

    images, original_coords = load_and_preprocess_images_square(image_path_list, img_load_resolution)

    import trimesh
    from vggt.dependency.np_to_pycolmap import batch_np_matrix_to_pycolmap, batch_np_matrix_to_pycolmap_wo_track

    model = load_demo_model(device)
    print("Model loaded")
    images = images.to(device)
    print(f"Loaded {len(images)} images from {image_dir}")

    # Run VGGT to estimate camera and depth
    # Run with 518x518 images
    extrinsic, intrinsic, depth_map, depth_conf = run_VGGT(model, images, dtype, vggt_fixed_resolution)
    points_3d = unproject_depth_map_to_point_map(depth_map, extrinsic, intrinsic)

    if args.use_ba:
        import pycolmap
        from vggt.dependency.track_predict import predict_tracks

        image_size = np.array(images.shape[-2:])
        scale = img_load_resolution / vggt_fixed_resolution
        shared_camera = args.shared_camera

        with torch.autocast("cuda", dtype=dtype, enabled=dtype is not None):
            # Predicting Tracks
            # Using VGGSfM tracker instead of VGGT tracker for efficiency
            # VGGT tracker requires multiple backbone runs to query different frames (this is a problem caused by the training process)
            # Will be fixed in VGGT v2

            # You can also change the pred_tracks to tracks from any other methods
            # e.g., from COLMAP, from CoTracker, or by chaining 2D matches from Lightglue/LoFTR.
            pred_tracks, pred_vis_scores, pred_confs, points_3d, points_rgb = predict_tracks(
                images,
                conf=depth_conf,
                points_3d=points_3d,
                masks=None,
                max_query_pts=args.max_query_pts,
                query_frame_num=args.query_frame_num,
                keypoint_extractor="aliked+sp",
                fine_tracking=args.fine_tracking,
            )

            torch.cuda.empty_cache()

        # rescale the intrinsic matrix from 518 to 1024
        intrinsic[:, :2, :] *= scale
        track_mask = pred_vis_scores > args.vis_thresh

        # TODO: radial distortion, iterative BA, masks
        reconstruction, valid_track_mask = batch_np_matrix_to_pycolmap(
            points_3d,
            extrinsic,
            intrinsic,
            pred_tracks,
            image_size,
            masks=track_mask,
            max_reproj_error=args.max_reproj_error,
            shared_camera=shared_camera,
            camera_type=args.camera_type,
            points_rgb=points_rgb,
        )

        if reconstruction is None:
            raise ValueError("No reconstruction can be built with BA")

        # Bundle Adjustment
        ba_options = pycolmap.BundleAdjustmentOptions()
        pycolmap.bundle_adjustment(reconstruction, ba_options)

        reconstruction_resolution = img_load_resolution
    else:
        conf_thres_value = args.conf_thres_value
        max_points_for_colmap = 100000  # randomly sample 3D points
        shared_camera = False  # in the feedforward manner, we do not support shared camera
        camera_type = "PINHOLE"  # in the feedforward manner, we only support PINHOLE camera

        image_size = np.array([vggt_fixed_resolution, vggt_fixed_resolution])
        num_frames, height, width, _ = points_3d.shape

        points_rgb = F.interpolate(
            images, size=(vggt_fixed_resolution, vggt_fixed_resolution), mode="bilinear", align_corners=False
        )
        points_rgb = (points_rgb.cpu().numpy() * 255).astype(np.uint8)
        points_rgb = points_rgb.transpose(0, 2, 3, 1)

        # (S, H, W, 3), with x, y coordinates and frame indices
        points_xyf = create_pixel_coordinate_grid(num_frames, height, width)

        conf_mask = depth_conf >= conf_thres_value
        # at most writing 100000 3d points to colmap reconstruction object
        conf_mask = randomly_limit_trues(conf_mask, max_points_for_colmap)

        points_3d = points_3d[conf_mask]
        points_xyf = points_xyf[conf_mask]
        points_rgb = points_rgb[conf_mask]

        print("Converting to COLMAP format")
        reconstruction = batch_np_matrix_to_pycolmap_wo_track(
            points_3d,
            points_xyf,
            points_rgb,
            extrinsic,
            intrinsic,
            image_size,
            shared_camera=shared_camera,
            camera_type=camera_type,
        )

        reconstruction_resolution = vggt_fixed_resolution

    reconstruction = rename_colmap_recons_and_rescale_camera(
        reconstruction,
        base_image_path_list,
        original_coords.numpy(),
        img_size=reconstruction_resolution,
        shift_point2d_to_original_res=True,
        shared_camera=shared_camera,
        coordinates_resolution=img_load_resolution,
    )

    point_cloud = trimesh.PointCloud(points_3d, colors=points_rgb)
    save_reconstruction(args, reconstruction, point_cloud, base_image_path_list)

    return True


def rename_colmap_recons_and_rescale_camera(
    reconstruction, image_paths, original_coords, img_size, shift_point2d_to_original_res=False, shared_camera=False,
    *, coordinates_resolution=None,
):
    """Map cameras and their observations from padded model images to the original images."""
    coordinates_scale = img_size / (coordinates_resolution or img_size)
    rescale_camera = True

    for pyimageid in reconstruction.images:
        pyimage = reconstruction.images[pyimageid]
        pycamera = reconstruction.cameras[pyimage.camera_id]
        pyimage.name = image_paths[pyimageid - 1]
        frame_coords = original_coords[pyimageid - 1]
        real_image_size = frame_coords[-2:]
        resize_ratio = max(real_image_size) / img_size
        top_left = frame_coords[:2] * coordinates_scale

        if rescale_camera:
            pred_params = pycamera.params * resize_ratio
            pred_params[-2:] -= top_left * resize_ratio
            pycamera.params = pred_params
            pycamera.width = int(real_image_size[0])
            pycamera.height = int(real_image_size[1])

        if shift_point2d_to_original_res:
            for point2D in pyimage.points2D:
                point2D.xy = (point2D.xy - top_left) * resize_ratio

        if shared_camera:
            # If shared_camera, all images share the same camera
            # no need to rescale any more
            rescale_camera = False

    return reconstruction


def main():
    args = parse_args()
    with torch.no_grad():
        demo_fn(args)

