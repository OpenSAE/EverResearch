"""Run depth estimation and export a prediction using the selected model."""

from tempfile import TemporaryDirectory

import numpy as np

from depth_anything_3.precheck import check_prediction_model, check_prediction_options
from depth_anything_3.runtime.experiments import record_precheck
from depth_anything_3.utils.export.npz import read_depth


def _predict(
    api, image, extrinsics, intrinsics, resolution, resize_method, feature_layers,
    infer_gs, use_ray_pose, ref_view_strategy,
):
    images, extrinsics, intrinsics = api._preprocess_inputs(
        image, extrinsics, intrinsics, resolution, resize_method
    )
    inputs, cameras, calibration = api._prepare_model_inputs(images, extrinsics, intrinsics)
    normalized = api._normalize_extrinsics(cameras.clone() if cameras is not None else None)
    raw_output = api._run_model_forward(
        inputs, normalized, calibration, feature_layers, infer_gs, use_ray_pose, ref_view_strategy
    )
    return api._convert_to_prediction(raw_output), images, extrinsics, intrinsics


def probe_prediction(
    api, image, extrinsics, intrinsics, resolution, resize_method, feature_layers,
    infer_gs, use_ray_pose, ref_view_strategy,
):
    """Predict and read back one view without retaining a scientific result."""
    sample, _, _, _ = _predict(
        api, image[:1], extrinsics[:1] if extrinsics is not None else None,
        intrinsics[:1] if intrinsics is not None else None,
        min(resolution, 56), resize_method, feature_layers, infer_gs,
        use_ray_pose, ref_view_strategy,
    )
    with TemporaryDirectory(prefix="da3-precheck-") as scratch:
        api._export_results(sample, "mini_npz", scratch)
        depth = read_depth(scratch, "mini_npz")
        if depth.ndim != 3 or depth.shape[0] != 1 or not np.isfinite(depth).all():
            raise ValueError("Precheck expected one finite depth map in the NPZ export")


def run_prediction(
    api,
    image,
    extrinsics,
    intrinsics,
    align_to_input_ext_scale,
    infer_gs,
    use_ray_pose,
    ref_view_strategy,
    render_exts,
    render_ixts,
    render_hw,
    process_res,
    process_res_method,
    export_dir,
    export_format,
    export_feat_layers,
    conf_thresh_percentile,
    num_max_points,
    show_cameras,
    feat_vis_fps,
    export_kwargs,
):
    export_feat_layers = list(export_feat_layers) if export_feat_layers is not None else []
    with record_precheck(samples_checked=1) as recorded:
        formats_to_check = export_format if export_dir is not None else "mini_npz"
        check_prediction_options(image, extrinsics, intrinsics, process_res, formats_to_check)
        check_prediction_model(api.model, infer_gs, formats_to_check)
        if recorded:
            probe_prediction(
                api, image, extrinsics, intrinsics,
                process_res, process_res_method, export_feat_layers, infer_gs,
                use_ray_pose, ref_view_strategy,
            )

    export_kwargs = {name: dict(options) for name, options in (export_kwargs or {}).items()}
    prediction, imgs_cpu, extrinsics, intrinsics = _predict(
        api, image, extrinsics, intrinsics, process_res, process_res_method,
        export_feat_layers, infer_gs, use_ray_pose, ref_view_strategy,
    )

    # Align prediction to extrinsincs
    prediction = api._align_to_input_extrinsics_intrinsics(
        extrinsics, intrinsics, prediction, align_to_input_ext_scale
    )

    # Add processed images for visualization
    prediction = api._add_processed_images(prediction, imgs_cpu)

    # Export if requested
    if export_dir is not None:

        if "gs" in export_format:
            if infer_gs and "gs_video" not in export_format:
                export_format = f"{export_format}-gs_video"
            if "gs_video" in export_format:
                if "gs_video" not in export_kwargs:
                    export_kwargs["gs_video"] = {}
                export_kwargs["gs_video"].update(
                    {
                        "extrinsics": render_exts,
                        "intrinsics": render_ixts,
                        "out_image_hw": render_hw,
                    }
                )
        # Add GLB export parameters
        if "glb" in export_format:
            if "glb" not in export_kwargs:
                export_kwargs["glb"] = {}
            export_kwargs["glb"].update(
                {
                    "conf_thresh_percentile": conf_thresh_percentile,
                    "num_max_points": num_max_points,
                    "show_cameras": show_cameras,
                }
            )
        # Add Feat_vis export parameters
        if "feat_vis" in export_format:
            if "feat_vis" not in export_kwargs:
                export_kwargs["feat_vis"] = {}
            export_kwargs["feat_vis"].update(
                {
                    "fps": feat_vis_fps,
                }
            )
        # Add COLMAP export parameters
        if "colmap" in export_format:
            if "colmap" not in export_kwargs:
                export_kwargs["colmap"] = {}
            export_kwargs["colmap"].update(
                {
                    "image_paths": image,
                    "conf_thresh_percentile": conf_thresh_percentile,
                    "process_res_method": process_res_method,
                }
            )
        api._export_results(prediction, export_format, export_dir, **export_kwargs)

    return prediction

