"""Run bounded checks through the selected depth workflow before formal execution."""

from contextlib import redirect_stdout
import json
from math import isfinite
from pathlib import Path
import random
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

from ...datasets.media.files import media_files


def inference_inputs(path, checkpoint, input_size, max_depth=None):
    if input_size is not None and input_size < 14:
        raise ValueError("Input size must be at least 14 pixels.")
    if max_depth is not None and (not isfinite(max_depth) or max_depth <= 0):
        raise ValueError("Maximum depth must be positive.")
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Model weights are missing: {checkpoint}")
    files = media_files(path)
    if not files:
        raise ValueError(f"No media files found at {path}")
    for source in files:
        if not source.is_file():
            raise FileNotFoundError(f"Input file is missing: {source}")
    return files


def inference_precheck(args, operation, files):
    """Exercise the task with one input and reopen its actual output formats."""
    import cv2
    import numpy as np
    from depth_anything_v2.weights import load_model

    start = perf_counter()
    model = load_model(args.encoder, args.load_from, getattr(args, "max_depth", None))
    ready = perf_counter()
    source = files[0]
    outputs = {}
    with TemporaryDirectory() as scratch:
        def output_path(_source, _index, name, suffix):
            path = Path(scratch) / f"{name}{suffix}"
            outputs[name] = path
            return path

        options = {"frame_limit": 1} if args.command == "video" else {}
        with redirect_stdout(sys.stderr):
            operation(args, model, [source], output_path, **options)

        if args.command == "video":
            capture = cv2.VideoCapture(str(outputs["depth_video"]))
            try:
                success, frame = capture.read()
                if not success or frame.size == 0:
                    raise ValueError("Cannot read the frame produced by the video precheck.")
            finally:
                capture.release()
        elif args.command == "pointcloud":
            import open3d as o3d

            cloud = o3d.io.read_point_cloud(str(outputs["point_cloud"]))
            points = np.asarray(cloud.points)
            if points.size == 0 or not cloud.has_colors() or not np.isfinite(points).all():
                raise ValueError("The point cloud precheck did not produce finite colored points.")
        else:
            if cv2.imread(str(outputs["depth_map"])) is None:
                raise ValueError("Cannot reopen the depth map produced by the precheck.")
            if "raw_depth_meter" in outputs:
                depth = np.load(outputs["raw_depth_meter"])
                if not np.isfinite(depth).all():
                    raise ValueError("The metric depth precheck produced non-finite values.")

    end = perf_counter()
    return model, {
        "samples_checked": 1,
        "input": str(source.resolve()),
        "checkpoint": str(args.load_from),
        "device": str(next(model.parameters()).device),
        "outputs_read": list(outputs),
        "model_load_seconds": ready - start,
        "operation_seconds": end - ready,
        "elapsed_seconds": end - start,
    }


def demo_precheck(args, sample):
    import numpy as np
    from PIL import Image
    from depth_anything_v2.weights import load_model

    from ..demo.interface import predict

    start = perf_counter()
    model = load_model(args.encoder, args.load_from)
    ready = perf_counter()
    with TemporaryDirectory() as scratch, Image.open(sample) as image:
        pixels = np.asarray(image.convert("RGB"))
        (_, preview), gray, raw = predict(model, pixels, scratch)
        if preview.shape != pixels.shape:
            raise ValueError("The demo comparison preview has incorrect dimensions.")
        for path, dtype in ((gray, np.uint8), (raw, np.uint16)):
            with Image.open(path) as output:
                array = np.asarray(output)
                if array.dtype != dtype or array.shape != pixels.shape[:2]:
                    raise ValueError("The demo precheck produced an invalid depth PNG.")
    end = perf_counter()
    return model, {
        "samples_checked": 1,
        "input": str(sample.resolve()),
        "checkpoint": str(args.load_from),
        "device": str(next(model.parameters()).device),
        "outputs_read": ["comparison_preview", "grayscale_depth", "raw_depth"],
        "model_load_seconds": ready - start,
        "operation_seconds": end - ready,
        "elapsed_seconds": end - start,
    }


def depth_order_precheck(args, dataset, score_image):
    """Confirm one annotated image can be decoded, scored, and read back."""
    from depth_anything_v2.weights import load_model

    start = perf_counter()
    model = load_model(args.encoder, args.load_from)
    ready = perf_counter()
    sample = dataset.names[0]
    correct, pairs = score_image(model, dataset, sample, args.input_size)
    with TemporaryDirectory() as scratch:
        result = Path(scratch) / "score.json"
        result.write_text(json.dumps({"correct": correct, "pairs": pairs}), encoding="utf-8")
        score = json.loads(result.read_text(encoding="utf-8"))
        if score["pairs"] == 0 or not 0 <= score["correct"] <= score["pairs"]:
            raise ValueError("The depth order precheck has no valid annotated pair.")
    end = perf_counter()
    return model, {
        "samples_checked": 1,
        "input": sample,
        "pairs_checked": pairs,
        "outputs_read": ["score"],
        "model_load_seconds": ready - start,
        "operation_seconds": end - ready,
        "elapsed_seconds": end - start,
    }


def training_inputs(args):
    if args.img_size < 14 or args.img_size % 14:
        raise ValueError("Training image size must be a positive multiple of 14.")
    if args.bs < 1 or args.epochs < 1 or not isfinite(args.lr) or args.lr <= 0:
        raise ValueError("Training epochs, batch size, and learning rate must be positive.")
    if not isfinite(args.min_depth) or not isfinite(args.max_depth) or not 0 < args.min_depth < args.max_depth:
        raise ValueError("Training requires finite depth limits with 0 < minimum < maximum.")
    if args.pretrained_from and not Path(args.pretrained_from).is_file():
        raise FileNotFoundError(f"Training weights are missing: {args.pretrained_from}")
    for split in (args.train_split, args.validation_split):
        entry = Path(split)
        if not entry.is_file():
            raise FileNotFoundError(f"Training split is missing: {entry}")
        lines = entry.read_text().splitlines()
        if not lines:
            raise ValueError(f"Training split is empty: {entry}")
        for line in lines:
            paths = line.split()
            if len(paths) != 2:
                raise ValueError(f"Expected an image path and a depth path in {entry}: {line}")
            for path in paths:
                if not Path(path).is_file():
                    raise FileNotFoundError(f"Training sample is missing: {path}. Supply local split lists.")


def training_precheck(args, device, world_size=1):
    """Exercise the real training and validation steps in isolated state."""
    import numpy as np
    import torch
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    from torch.utils.tensorboard import SummaryWriter

    from ..training.loss import SiLogLoss
    from ..training.train import train_step, training_datasets, training_model, training_optimizer, validation_step

    if not torch.cuda.is_available() or device.index >= torch.cuda.device_count():
        raise ValueError("Metric-depth training requires an available CUDA GPU.")
    start = perf_counter()
    training, validation = training_datasets(args)
    samples_per_rank = (len(training) + world_size - 1) // world_size
    if samples_per_rank < args.bs:
        raise ValueError(f"The {len(training)} training pairs cannot fill batch size {args.bs} on {world_size} GPU(s).")
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    try:
        with torch.random.fork_rng(devices=[device.index]):
            random.seed(0)
            np.random.seed(0)
            torch.random.default_generator.manual_seed(0)
            with torch.cuda.device(device):
                torch.cuda.manual_seed(0)
            model = training_model(args).to(device).train()
            optimizer = training_optimizer(model, args.lr)
            torch.cuda.synchronize(device)
            ready = perf_counter()
            train_sample = training[0]
            train_batch = {key: value.unsqueeze(0) for key, value in train_sample.items() if key != "image_path"}
            loss = train_step(args, train_batch, model, SiLogLoss().to(device), optimizer, device)
            if not isfinite(loss) or not optimizer.state:
                raise ValueError("The first training pair did not produce a finite loss and optimizer step.")
            model.eval()
            metrics = None
            for validation_index in range(min(4, len(validation))):
                sample = validation[validation_index]
                validation_batch = {key: value.unsqueeze(0) for key, value in sample.items() if key != "image_path"}
                metrics = validation_step(args, validation_batch, model, device)
                if metrics is not None:
                    break
            if metrics is None or not all(isfinite(value) for value in metrics.values()):
                raise ValueError("The validation precheck found no finite metrics in the first four available pairs.")

            with TemporaryDirectory() as scratch:
                with SummaryWriter(scratch) as writer:
                    writer.add_scalar("train/loss", loss)
                    for name, value in metrics.items():
                        writer.add_scalar(f"eval/{name}", value)
                events = EventAccumulator(scratch).Reload()
                tags = events.Tags()["scalars"]
                if set(tags) != {"train/loss", *(f"eval/{name}" for name in metrics)} or not all(
                    isfinite(events.Scalars(tag)[0].value) for tag in tags
                ):
                    raise ValueError("The training precheck could not read finite TensorBoard results.")
            end = perf_counter()
    finally:
        random.setstate(python_state)
        np.random.set_state(numpy_state)

    return {
        "samples_checked": validation_index + 2,
        "training_pairs": 1,
        "training_input": train_sample["image_path"],
        "validation_pairs": validation_index + 1,
        "validation_input": sample["image_path"],
        "optimizer_steps": 1,
        "device": str(device),
        "train_loss": loss,
        "validation_metrics": metrics,
        "outputs_read": tags,
        "model_load_seconds": ready - start,
        "operation_seconds": end - ready,
        "elapsed_seconds": end - start,
    }
