"""Run point-prompt image segmentation and read the recorded prediction arrays."""

import argparse
import json
import math
import re
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from uuid import uuid4

import numpy as np
import torch
from omegaconf import OmegaConf

from sam2.build_sam import (
    build_sam2,
    compose_sam2_model_config,
    HF_MODEL_ID_TO_FILENAMES,
)
from sam2.config import load_config
from sam2.precheck.gate import check_image
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.workspace import checkpoint_path, project_workspace

MODELS = {
    model_id.split("/", 1)[1]: files
    for model_id, files in HF_MODEL_ID_TO_FILENAMES.items()
}
TASK = "image_segmentation"


def dataset_name(value):
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("use a dataset name such as notebook_images")
    return value


def experiment_name(value):
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", value) or value in {
        "default",
        "experiment",
        "run",
        "test",
        "trial",
    }:
        raise argparse.ArgumentTypeError(
            "use one to three words describing the experiment, such as point_prompt"
        )
    return value


def read_result(path):
    """Read one saved prediction and return its settings and prediction arrays."""
    with np.load(path, allow_pickle=False) as result:
        if result["format_version"].item() != 1:
            raise ValueError(f"Unsupported image prediction format in {path}")
        return (
            json.loads(result["metadata"].item()),
            result["masks"],
            result["scores"],
            result["low_res_logits"],
        )


def predict_image(settings, prepared=None):
    checkpoint, image, device = prepared if prepared is not None else check_image(settings)
    model = build_sam2(settings["config"], ckpt_path=checkpoint, device=device)
    predictor = SAM2ImagePredictor(model)
    autocast = (
        torch.autocast("cuda", dtype=torch.bfloat16)
        if device.type == "cuda"
        else nullcontext()
    )
    with torch.inference_mode(), autocast:
        predictor.set_image(image)
        return predictor.predict(
            point_coords=np.array([point[:2] for point in settings["points"]]),
            point_labels=np.array([point[2] for point in settings["points"]]),
            multimask_output=settings["multimask_output"],
        )


def save_execution(settings, precheck_seconds, prediction=None, rejection=None):
    finished = datetime.now(timezone.utc)
    run_id = f"{finished:%Y%m%dT%H%M%S}.{finished.microsecond:06d}Z-{uuid4().hex}"
    execution_root = Path(settings["experiment_dir"]) / "executions"
    execution_root.mkdir(parents=True, exist_ok=True)
    destination = execution_root / run_id
    artifact = Path("artifacts/prediction.npz")
    metadata = {
        **settings,
        "run_id": run_id,
        "finished_at": finished.isoformat(),
        "torch_version": str(torch.__version__),
    }
    with TemporaryDirectory(prefix=".prediction-", dir=execution_root) as staging:
        staged = Path(staging) / run_id
        staged.mkdir()
        outputs = {}
        manifest = {
            "run_id": run_id,
            "subname": settings["name"],
            "status": "failed" if rejection else "succeeded",
            "formal_started": rejection is None,
            "precheck_seconds": precheck_seconds,
            "effective_config": "config.json",
            "outputs": outputs,
        }
        if rejection is not None:
            manifest["diagnostics"] = [{"stage": "automatic_precheck", "message": rejection}]
        else:
            masks, scores, low_res_logits = prediction
            (staged / artifact.parent).mkdir()
            np.savez_compressed(
                staged / artifact,
                format_version=1,
                metadata=json.dumps(metadata),
                masks=masks,
                scores=scores,
                low_res_logits=low_res_logits,
            )
            _, stored_masks, stored_scores, stored_logits = read_result(staged / artifact)
            if (stored_masks.shape, stored_scores.shape, stored_logits.shape) != (
                masks.shape, scores.shape, low_res_logits.shape
            ):
                raise ValueError("Prediction readback returned unexpected array shapes")
            report = Path("reports/precheck.json")
            (staged / report.parent).mkdir()
            (staged / report).write_text(json.dumps({"samples_checked": 1}, indent=2))
            outputs.update(prediction=artifact.as_posix(), precheck=report.as_posix())
        (staged / "config.json").write_text(json.dumps(settings, indent=2))
        (staged / "manifest.json").write_text(json.dumps(manifest, indent=2))
        staged.rename(destination)
    return destination if rejection is not None else destination / artifact


def main(argv=None):
    started = perf_counter()
    project_root = project_workspace()
    defaults = load_config().image
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--print-config", action="store_true", help="show settings and exit"
    )
    mode.add_argument(
        "--read-result", type=Path, help="inspect one saved .npz prediction"
    )
    parser.add_argument("--image", type=Path, help="image to segment")
    parser.add_argument("--dataset", type=dataset_name, help="source of the image")
    parser.add_argument(
        "--point",
        nargs=3,
        type=float,
        action="append",
        metavar=("X", "Y", "LABEL"),
        help="pixel coordinates with label 1 (foreground) or 0 (background); repeatable",
    )
    parser.add_argument("--model", choices=MODELS, default=defaults.model)
    parser.add_argument(
        "--checkpoint", type=Path, help="path to a local model checkpoint"
    )
    parser.add_argument(
        "--device", default=defaults.device, help="PyTorch device (default: cuda)"
    )
    parser.add_argument(
        "--single-mask", action="store_true", help="return one mask instead of three"
    )
    parser.add_argument("--name", type=experiment_name, default=defaults.purpose)
    parser.add_argument(
        "--experiment-root", type=Path, default=project_root / "experiment" if project_root else None
    )
    args = parser.parse_args(argv)

    if args.read_result is not None:
        try:
            metadata, masks, scores, logits = read_result(args.read_result)
        except (OSError, KeyError, ValueError) as exc:
            parser.error(f"Cannot read {args.read_result}: {exc}")
        print(
            json.dumps(
                {
                    **metadata,
                    "mask_shape": list(masks.shape),
                    "scores": scores.tolist(),
                    "low_res_logits_shape": list(logits.shape),
                },
                indent=2,
            )
        )
        return

    points = []
    for x, y, label in args.point or ():
        if not (math.isfinite(x) and math.isfinite(y) and label in (0, 1)):
            parser.error(
                "--point needs finite X and Y coordinates and a label of 0 or 1"
            )
        points.append([x, y, int(label)])

    config, checkpoint = MODELS[args.model]
    model_family, model_variant = args.model.split("-", 1)
    model_path = f"{model_family.replace('.', '_')}_{model_variant.replace('-', '_')}"
    experiment_dir = None
    if args.dataset and args.experiment_root is not None:
        experiment_dir = (
            args.experiment_root.resolve()
            / args.dataset
            / model_path
            / TASK
            / args.name
        )
    settings = {
        "task": TASK,
        "name": args.name,
        "component_paths": {"model": model_path},
        "dataset": args.dataset,
        "model": args.model,
        "config": config,
        "model_config": OmegaConf.to_container(compose_sam2_model_config(config).model),
        "checkpoint": str(
            (args.checkpoint or checkpoint_path(checkpoint)).resolve()
        ),
        "device": args.device,
        "image": str(args.image.resolve()) if args.image else None,
        "points": points,
        "multimask_output": not args.single_mask,
        "experiment_dir": str(experiment_dir) if experiment_dir else None,
    }
    if args.print_config:
        print(json.dumps(settings, indent=2))
        return
    if not (args.image and args.dataset and points):
        parser.error("prediction requires --image, --dataset and at least one --point")
    if experiment_dir is None:
        parser.error("prediction outside a checkout requires --experiment-root")
    try:
        prepared = check_image(settings)
    except (OSError, ValueError) as exc:
        directory = save_execution(settings, perf_counter() - started, rejection=str(exc))
        parser.error(f"{exc}. Precheck record: {directory}")
    try:
        precheck_seconds = perf_counter() - started
        prediction = predict_image(settings, prepared)
        print(save_execution(settings, precheck_seconds, prediction=prediction))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
