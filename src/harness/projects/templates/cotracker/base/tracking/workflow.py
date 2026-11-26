"""Connect tracking options, input decoding, pretrained weights, precheck, and run records."""

from pathlib import Path
import os
import sys
from time import monotonic

import numpy as np
import torch
import yaml

from cotracker.configuration import configuration_path
from cotracker.datasets.video import read_video_from_path
from cotracker.hub_api import COTRACKER3_SCALED_OFFLINE_URL, cotracker3_offline
from cotracker.precheck.tracking import precheck_tracking
from cotracker.predictor import CoTrackerPredictor
from cotracker.records import TrackingRun, write_json
from cotracker.tracking.points import select_device, track_points, write_overlay


def configuration_for(args):
    workspace = Path(args.workspace).expanduser().resolve()
    config_file = workspace / "conf" / "config.yaml"
    if not config_file.is_file():
        config_file = configuration_path(
            Path(__file__).resolve().parents[2] / "conf/config.yaml",
            "config_data", "config.yaml",
        )
    config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    config.pop("catalogs")
    for key in ("video", "grid_size", "grid_query_frame", "backward_tracking", "device", "subname"):
        if (value := getattr(args, key)) is not None:
            config[key] = value
    if args.video is None:
        config["video"] = str(workspace / config["video"])
    else:
        config["video"] = str(Path(config["video"]).expanduser().resolve())
    checkpoint = args.checkpoint or os.getenv("COTRACKER_OFFLINE_CHECKPOINT")
    config["checkpoint"] = str(Path(checkpoint).expanduser().resolve()) if checkpoint else COTRACKER3_SCALED_OFFLINE_URL
    return workspace, config


def run_tracking(args, precheck_only=False):
    workspace, configuration = configuration_for(args)
    device = select_device(configuration["device"])
    configuration["device"] = str(device)
    if args.print_config:
        return configuration

    run = None if precheck_only else TrackingRun(workspace, configuration)
    environment = {"python": sys.version.split()[0], "torch": str(torch.__version__), "device": str(device)}
    formal_started = False
    precheck_started = monotonic()
    outputs = {}
    try:
        frames = read_video_from_path(configuration["video"])
        if frames is None:
            raise ValueError(f"Could not decode video {configuration['video']}")
        checkpoint = configuration["checkpoint"]
        if checkpoint == COTRACKER3_SCALED_OFFLINE_URL:
            model = cotracker3_offline()
        else:
            model = CoTrackerPredictor(checkpoint=checkpoint, window_len=60)
        model = model.to(device)
        check = precheck_tracking(model, frames, device, configuration)
        if precheck_only:
            return check

        outputs["precheck"] = "reports/precheck.json"
        write_json(run.directory / outputs["precheck"], check)
        run.write("running", precheck=check, precheck_seconds=monotonic() - precheck_started,
                  environment=environment, outputs=outputs, formal_started=True)
        formal_started = True
        video, tracks, visibility = track_points(
            model, frames, device, configuration["grid_size"], configuration["grid_query_frame"],
            configuration["backward_tracking"],
        )
        staging = run.directory / "tmp"
        staging.mkdir()
        np.savez_compressed(staging / "tracks.npz", tracks=tracks.cpu().numpy(),
                            visibility=visibility.cpu().numpy())
        query_frame = 0 if configuration["backward_tracking"] else configuration["grid_query_frame"]
        write_overlay(staging, video, tracks, visibility, query_frame)
        staging.rename(run.directory / "artifacts")
        outputs.update(tracks="artifacts/tracks.npz", video="artifacts/video.mp4")
        run.write("succeeded", outputs=outputs)
    except BaseException as error:
        if run is not None:
            stage = "formal_execution" if formal_started else "automatic_precheck"
            run.write("interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
                      formal_started=formal_started, environment=environment,
                      outputs=outputs, diagnostics=[{"stage": stage, "message": str(error)}])
        raise
    return {"run_directory": str(run.directory), **run.manifest}
