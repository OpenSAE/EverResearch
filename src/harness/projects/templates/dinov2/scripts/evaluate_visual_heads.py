"""Evaluate released DINOv2 depth and linear semantic heads on local datasets.

NYU input contains rgb PNG files and depth arrays in metres. ADE20K input is
the publisher's validation image and annotation directories. Use --sample to
select evenly spaced records and preserve a bounded, reproducible run.
"""

import argparse
import json
from pathlib import Path
import time

START = time.perf_counter()

import numpy as np
from PIL import Image
import torch
from torch import nn
import torch.nn.functional as F
from torchvision.transforms import InterpolationMode, Resize
from torchvision.transforms.functional import pil_to_tensor

from dinov2.hub.backbones import dinov2_vits14
from dinov2.hub.depthers import dinov2_vits14_ld
from dinov2.hub.utils import CenterPadding


def load_inputs(image_root, suffix, sample):
    paths = sorted(image_root.glob(f"*{suffix}"))
    if not paths:
        raise ValueError(f"No {suffix} images in {image_root}")
    if sample:
        paths = [paths[index] for index in np.linspace(0, len(paths) - 1, min(sample, len(paths)), dtype=int)]
    return paths


def normalize(image):
    values = pil_to_tensor(image).cuda().float()
    mean = values.new_tensor([123.675, 116.28, 103.53])[:, None, None]
    std = values.new_tensor([58.395, 57.12, 57.375])[:, None, None]
    return ((values - mean) / std)[None]


class SemanticHead(nn.Module):
    """Run the publisher's single-scale ADE20K linear head with slide inference."""

    def __init__(self, checkpoint):
        super().__init__()
        self.backbone = dinov2_vits14()
        self.padding = CenterPadding(self.backbone.patch_size)
        self.bn = nn.BatchNorm2d(384)
        self.conv_seg = nn.Conv2d(384, 150, 1)
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)["state_dict"]
        parameters = {key.removeprefix("decode_head."): value for key, value in state.items()}
        loaded = self.load_state_dict(parameters, strict=False)
        if loaded.unexpected_keys or any(not key.startswith("backbone.") for key in loaded.missing_keys):
            raise ValueError(f"Invalid ADE20K linear head: {loaded}")

    def forward(self, image, native_size):
        height, width = image.shape[-2:]
        crop_size, stride = 512, 341
        summed = image.new_zeros((1, 150, height, width))
        counts = image.new_zeros((1, 1, height, width))
        for y in range(0, max(height - crop_size + stride - 1, 0) // stride + 1):
            for x in range(0, max(width - crop_size + stride - 1, 0) // stride + 1):
                bottom = min(y * stride + crop_size, height)
                right = min(x * stride + crop_size, width)
                top = max(0, bottom - crop_size)
                left = max(0, right - crop_size)
                crop = self.padding(image[:, :, top:bottom, left:right])
                (features,) = self.backbone.get_intermediate_layers(crop, n=[11], reshape=True)
                logits = self.conv_seg(self.bn(features))
                logits = F.interpolate(logits, size=(bottom - top, right - left), mode="bilinear", align_corners=False)
                summed[:, :, top:bottom, left:right] += logits
                counts[:, :, top:bottom, left:right] += 1
        scores = F.interpolate(summed / counts, size=native_size, mode="bilinear", align_corners=False)
        return scores.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)


def make_model(task, weights):
    if task == "semantic":
        return SemanticHead(weights / "dinov2_vits14_ade20k_linear_head.pth")
    # The released archive contains a NumPy float32 summary statistic in its metadata.
    scalar = (np._core.multiarray.scalar, "numpy.core.multiarray.scalar")
    with torch.serialization.safe_globals([scalar, np.dtype, np.dtypes.Float32DType]):
        model = dinov2_vits14_ld(weights="NYU")
    # The standalone Hub factory defaults its shared linear head to 80 m.
    # Meta's NYU head configuration defines depth bins over 0.001–10 m.
    model.decode_head.max_depth = 10.0
    return model


@torch.inference_mode()
def evaluate(args):
    torch.set_num_threads(4)
    torch.hub.set_dir(str(args.weights.parent))
    model = make_model(args.task, args.weights).eval().cuda()
    resize = Resize(512, interpolation=InterpolationMode.BILINEAR)
    depth = args.task == "depth"
    annotations = args.dataset_root / ("depth" if depth else "annotations/validation")
    images = load_inputs(args.dataset_root / ("rgb" if depth else "images/validation"),
                         ".png" if depth else ".jpg", args.sample)
    predictions = args.output / "artifacts" / "predictions"
    reports = args.output / "reports"
    predictions.mkdir(parents=True, exist_ok=False)
    reports.mkdir(parents=True, exist_ok=True)
    torch.cuda.synchronize()
    startup = time.perf_counter() - START
    confusion = np.zeros((150, 150), dtype=np.int64)
    rmse = []
    timings = []
    for path in images:
        before = time.perf_counter()
        with Image.open(path) as source:
            image = source.convert("RGB")
        if depth:
            tensor = normalize(image)
            prediction = (model.encode_decode(tensor, None)
                          + model.encode_decode(tensor.flip((-1,)), None).flip((-1,))) * 0.5
            prediction = prediction[0, 0].cpu().numpy()
            target = np.load(annotations / f"{path.stem}.npy")
            valid = np.isfinite(target) & (target > 0.001) & (target < 10)
            # Eigen crop in the original 480 × 640 NYU image coordinates.
            valid[:45] = valid[471:] = False
            valid[:, :41] = valid[:, 601:] = False
            rmse.append(float(np.sqrt(np.mean(np.square(prediction[valid] - target[valid])))))
            np.save(predictions / f"{path.stem}.npy", prediction)
        else:
            prediction = model(normalize(resize(image)), (image.height, image.width))
            with Image.open(annotations / f"{path.stem}.png") as label:
                target = np.array(label, dtype=np.int64)
            valid = (target > 0) & (target <= 150)
            classes = (target[valid] - 1) * 150 + prediction[valid]
            confusion += np.bincount(classes, minlength=150 * 150).reshape(150, 150)
            Image.fromarray(prediction + 1).save(predictions / f"{path.stem}.png")
        timings.append({"image": path.name, "seconds": time.perf_counter() - before})
    if depth:
        metrics = {"mean_image_rmse_metres": float(np.mean(rmse))}
    else:
        true_positive = confusion.diagonal()
        union = confusion.sum(axis=0) + confusion.sum(axis=1) - true_positive
        present = union > 0
        metrics = {"mean_iou": float(np.mean(true_positive[present] / union[present])),
                   "classes_with_union": int(np.count_nonzero(present))}
    (args.output / "artifacts" / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    runtime = {"sample_count": len(timings), "batch_size": 1, "loader_workers": 0,
               "startup_seconds": startup, "elapsed_seconds": time.perf_counter() - START,
               "model": "DINOv2 ViT-S/14", "torch": torch.__version__, "cuda": torch.version.cuda,
               "gpu": torch.cuda.get_device_name(), "samples": timings}
    (reports / "runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")
    print(json.dumps({**metrics, "sample_count": len(timings), "seconds": runtime["elapsed_seconds"]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=("depth", "semantic"))
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample", type=int)
    args = parser.parse_args()
    if args.sample is not None and args.sample < 1:
        parser.error("--sample must be positive")
    evaluate(args)


if __name__ == "__main__":
    main()
