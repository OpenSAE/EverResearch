"""Validate the selected inputs and model capabilities before task computation."""

from pathlib import Path

from depth_anything_3.runtime.paths import find_checkout
from depth_anything_3.streaming_frames import streaming_frames
from depth_anything_3.utils.export import SUPPORTED_EXPORT_FORMATS


def check_prediction_options(image, extrinsics, intrinsics, process_res, export_format):
    """Check the view batch, calibration alignment, and requested export capabilities."""
    if not len(image):
        raise ValueError("Provide at least one image")
    if process_res <= 0:
        raise ValueError("Processing resolution must be positive")
    for name, cameras in (("extrinsics", extrinsics), ("intrinsics", intrinsics)):
        if cameras is not None and len(cameras) != len(image):
            raise ValueError(f"Provide one set of {name} per input image")
    if extrinsics is not None and intrinsics is None:
        raise ValueError("Camera intrinsics are required with extrinsics")
    unknown_formats = set(export_format.split("-")) - SUPPORTED_EXPORT_FORMATS
    if unknown_formats:
        raise ValueError(f"Unsupported export formats: {', '.join(sorted(unknown_formats))}")
    if "colmap" in export_format and not all(isinstance(view, str) for view in image):
        raise ValueError("COLMAP export requires a file path for each input image")


def check_prediction_model(model, infer_gs, export_format):
    """Validate the capabilities of the selected depth network."""
    if "gs" in export_format and not infer_gs:
        raise ValueError("Set infer_gs=True for Gaussian splatting export")
    network = getattr(model, "da3", model)
    if infer_gs and getattr(network, "gs_head", None) is None:
        raise ValueError("Gaussian splatting requires a model with a Gaussian head")


def check_streaming(image_dir, config):
    """Check the frame source, chunk overlap, and required local model resources."""
    streaming_frames(image_dir)
    model = config["Model"]
    if not 0 < model["overlap"] < model["chunk_size"]:
        raise ValueError("Streaming overlap must be positive and smaller than the chunk size")
    required = ["DA3", "DA3_CONFIG"]
    if model["loop_enable"]:
        checkout = find_checkout()
        if checkout is None or not (checkout / "third_party/salad/models").is_dir():
            raise ValueError("Initialize the SALAD submodule to enable streaming loop detection")
        required.append("SALAD")
    for name in required:
        path = Path(config["Weights"][name])
        if not path.is_file():
            raise FileNotFoundError(f"Missing streaming weight or configuration {name}: {path}")


def check_benchmark(datasets, modes, supported_modes, registry):
    """Validate benchmark selection and the dataset roots before allocating model resources."""
    unknown_modes = modes - supported_modes
    if unknown_modes:
        raise ValueError(f"Unknown modes: {sorted(unknown_modes)}. Valid: {sorted(supported_modes)}")
    readers = registry.all()
    selected = {}
    for name in datasets:
        if name not in readers:
            raise ValueError(f"Dataset {name!r} not found. Available: {sorted(readers)}")
        reader = readers[name]
        if not Path(reader.data_root).is_dir():
            raise FileNotFoundError(f"Benchmark data for {name!r} is missing: {reader.data_root}")
        selected[name] = reader
    return selected
