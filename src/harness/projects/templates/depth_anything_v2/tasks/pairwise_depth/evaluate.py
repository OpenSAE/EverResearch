"""Score the DA-2K closer-point annotations and record timing in an experiment.

Run with the installed depth model and a local publisher dataset extraction.
"""

import argparse
from collections import defaultdict
import json
from pathlib import Path
from time import perf_counter

import numpy as np

from depth_anything_v2.weights import ENCODERS

from ...datasets.da_benchmark.dataset import DepthOrderDataset
from ...records import RunRecord, effective_options, write_json
from ..precheck.check import depth_order_precheck


def score_image(model, dataset, name, input_size):
    image, pairs = dataset.read(name)
    depth = model.infer_image(image, input_size)
    if not np.isfinite(depth).all():
        raise ValueError(f"Non-finite relative depth for {name}")
    correct = 0
    for pair in pairs:
        closer = pair["closer_point"]
        if closer not in ("point1", "point2"):
            raise ValueError(f"Unknown closer-point label in {name}")
        farther = "point2" if closer == "point1" else "point1"
        points = tuple(tuple(pair[key]) for key in (closer, farther))
        if any(not (0 <= y < depth.shape[0] and 0 <= x < depth.shape[1]) for y, x in points):
            raise ValueError(f"An annotated pixel is outside {name}")
        correct += int(depth[points[0]] > depth[points[1]])
    return correct, len(pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--load-from", required=True, type=Path)
    parser.add_argument("--encoder", choices=ENCODERS, default="vitl")
    parser.add_argument("--input-size", type=int, default=518)
    parser.add_argument("--sample-list", type=Path, help="Limit scoring to the listed source image paths")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--study", default="relative_benchmark")
    parser.add_argument("--precheck", action="store_true", help="Score and reopen one annotated image without creating a run")
    args = parser.parse_args()
    args.outdir = None
    dataset = DepthOrderDataset(args.dataset_root, args.sample_list)
    names = dataset.names
    if args.input_size < 14:
        raise ValueError("Input size must be at least 14 pixels.")

    encoders = {"vits": "small", "vitb": "base", "vitl": "large", "vitg": "giant"}
    config = effective_options(args)
    config.update(dataset="da_benchmark", model=f"depth_anything_{encoders[args.encoder]}", task="pairwise_depth")
    record = None if args.precheck else RunRecord(
        args, config, [dataset.annotation_file, *(dataset.path(name) for name in names)]
    )
    try:
        model, precheck_report = depth_order_precheck(args, dataset, score_image)
        if args.precheck:
            print(json.dumps({**config, "precheck_report": precheck_report}, indent=2))
            return
        record.start_work(precheck_report)
        ready = perf_counter()
        scenes = defaultdict(lambda: {"images": 0, "pairs": 0, "correct": 0})
        timings = []
        for name in names:
            begin = perf_counter()
            group = scenes[Path(name).parts[1]]
            correct, pairs = score_image(model, dataset, name, args.input_size)
            group["correct"] += correct
            group["images"] += 1
            group["pairs"] += pairs
            timings.append({"image": name, "seconds": perf_counter() - begin})
        for group in scenes.values():
            group["accuracy"] = group["correct"] / group["pairs"]
        results = {
            "images": len(names),
            "pairs": sum(group["pairs"] for group in scenes.values()),
            "scenario_accuracy_mean": float(np.mean([group["accuracy"] for group in scenes.values()])),
            "scenarios": dict(scenes),
            "sample_timings": timings,
            "model_load_seconds": precheck_report["model_load_seconds"],
            "precheck_seconds": precheck_report["elapsed_seconds"],
            "scoring_seconds": perf_counter() - ready,
        }
        write_json(record.artifact("benchmark_scores", ".json"), results)
    except KeyboardInterrupt as error:
        if record is not None:
            record.finish("interrupted", error)
        raise
    except Exception as error:
        if record is not None:
            record.finish("failed", error)
        raise
    record.finish("succeeded")
    print(record.directory)


if __name__ == "__main__":
    main()
