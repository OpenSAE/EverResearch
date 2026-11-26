"""Measure ACT request timing with published Aloha demonstrations.

Use a local LeRobot dataset and a prepared ACT checkpoint to benchmark the public
Zenoh policy server on loopback. The client sends observations and checks actions
without connecting to any robot.
"""

import argparse
import json
import subprocess
import time
from pathlib import Path
from uuid import uuid4

import numpy as np
import yaml

from lerobot.datasets import LeRobotDataset
from lerobot.inference import (
    ChunkRequest,
    ExecutionMode,
    FeatureSpec,
    ObservationSnapshot,
    RemoteInferenceConfig,
)
from lerobot.policies import QueueSnapshot
from lerobot.remote_inference.client import RemoteClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--port", type=int, default=17447)
    args = parser.parse_args()

    started = time.perf_counter()
    dataset = LeRobotDataset(
        "lerobot/aloha_sim_transfer_cube_human", root=args.dataset_root, video_backend="pyav"
    )
    if not 1 <= args.requests <= len(dataset):
        parser.error(f"--requests must be between 1 and the dataset size ({len(dataset)})")
    args.output.mkdir(parents=True, exist_ok=True)
    semantics = "aloha-simulation-joint-position"
    endpoint = f"tcp/127.0.0.1:{args.port}"
    names = tuple(dataset.meta.features["observation.state"]["names"]["motors"])
    features = (
        FeatureSpec("observation.state", (14,), "float32", names=names, semantics=semantics),
        FeatureSpec("observation.images.top", (480, 640, 3), "uint8", kind="rgb", semantics="rgb-overhead"),
    )
    action = FeatureSpec("action", (14,), "float32", names=names, semantics=semantics)
    config = {
        "deployment": "aloha_benchmark",
        "model": {"repo_or_path": str(args.policy.resolve()), "device": "cuda"},
        "execution": {"supported_modes": ["chunk"], "action_fps": 50.0},
        "zenoh": {"mode": "peer", "listen_endpoints": [endpoint]},
        "semantics": semantics,
        "robot_type": "aloha",
        "features": [vars(feature) for feature in features],
        "action_feature": vars(action),
    }
    config_path = args.output / "server_config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    rows = []
    with (args.output / "server.log").open("w", encoding="utf-8") as log:
        server = subprocess.Popen(
            ["lerobot-policy-server", f"--config_path={config_path}"], stdout=log, stderr=subprocess.STDOUT
        )
        try:
            deadline = started + 60.0
            while "Policy server ready:" not in Path(log.name).read_text(encoding="utf-8"):
                if server.poll() is not None or time.perf_counter() >= deadline:
                    raise RuntimeError(f"Policy server startup failed. See {log.name}.")
                time.sleep(0.05)
            ready = time.perf_counter()
            client = RemoteClient.connect(
                RemoteInferenceConfig(
                    endpoint=endpoint, deployment="aloha_benchmark", semantics=semantics, chunk_merge="append"
                )
            )
            try:
                client.admit(
                    features=features,
                    action_feature=action,
                    semantics=semantics,
                    action_interval=0.02,
                    mode="chunk",
                )
                admitted = time.perf_counter()
                continuation = QueueSnapshot(0, 0, 0, None, None, ())
                for index in np.linspace(0, len(dataset) - 1, args.requests, dtype=int).tolist():
                    before_read = time.perf_counter()
                    frame = dataset[index]
                    image = (frame["observation.images.top"] * 255).round().byte().permute(1, 2, 0).numpy()
                    observation = ObservationSnapshot(
                        {
                            "observation.state": frame["observation.state"].numpy(),
                            "observation.images.top": image,
                        },
                        time.monotonic(),
                        frame["task"],
                        observation_id=str(index),
                    )
                    before_inference = time.perf_counter()
                    result = client.infer(
                        ChunkRequest(
                            observation,
                            continuation,
                            uuid4().hex,
                            client.generation,
                            ExecutionMode.CHUNK,
                            0,
                            before_inference,
                        )
                    )
                    received = time.perf_counter()
                    if (
                        result.canonical_actions.shape != (100, 14)
                        or not result.canonical_actions.isfinite().all()
                    ):
                        raise ValueError(f"Invalid action chunk for frame {index}")
                    rows.append(
                        {
                            "frame_index": index,
                            "episode_index": int(frame["episode_index"]),
                            "read_s": before_inference - before_read,
                            "request_s": received - before_inference,
                            "server_durations": result.server_durations,
                        }
                    )
            finally:
                client.close()
        finally:
            server.terminate()
            server.wait(timeout=20)

    timings = [row["request_s"] for row in rows]
    report = {
        "artifact_identity": client.artifact_identity,
        "startup_s": ready - started,
        "handshake_s": admitted - ready,
        "total_s_before_report": time.perf_counter() - started,
        "request_median_s": float(np.median(timings)),
        "request_p95_s": float(np.percentile(timings, 95)),
        "requests": rows,
    }
    (args.output / "request_timings.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
