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
#
# Adapted from [VGGT-Long](https://github.com/DengKaiCQ/VGGT-Long)

"""Start DA3 Streaming and preview its resolved paths without loading inference dependencies."""

import argparse
from datetime import datetime
from pathlib import Path

import yaml
from depth_anything_3.runtime.paths import CONFIG_ROOT, checkout_default
from depth_anything_3.runtime.streaming_config import load_config
from depth_anything_3.precheck import check_streaming


def main(argv=None):
    parser = argparse.ArgumentParser(description="DA3-Streaming")
    parser.add_argument("--image_dir", required=True, help="Directory of input frames")
    parser.add_argument(
        "--config",
        help="Custom streaming YAML configuration",
    )
    parser.add_argument("--preset", default="base_config", choices=["base_config", "tum", "kitti"])
    parser.add_argument("--output_dir", help="Output directory")
    parser.add_argument("--show-config", action="store_true", help="Print settings without running")
    args = parser.parse_args(argv)
    config_path = Path(args.config) if args.config else CONFIG_ROOT / "tasks" / "streaming" / "config.yaml"
    config = load_config(config_path)
    if args.config is None:
        config = config[args.preset]
        config["Weights"] = {
            name: checkout_default(path) for name, path in config["Weights"].items()
        }
    output = args.output_dir
    if output is None:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output = str(Path(checkout_default("exps")) / args.image_dir.replace("/", "_") / timestamp)

    if args.show_config:
        settings = {
            "image_dir": str(Path(args.image_dir).resolve()),
            "config_path": str(config_path.resolve()),
            "output_dir": str(Path(output).resolve()),
            **config,
        }
        print(yaml.safe_dump(settings, sort_keys=False), end="")
        return

    try:
        check_streaming(args.image_dir, config)
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))
    from depth_anything_3.streaming_task.pipeline import run_streaming

    run_streaming(args.image_dir, output, config)


def __getattr__(name):
    """Keep the legacy module import for the streaming implementation."""
    if name in {"DA3_Streaming", "depth_to_point_cloud_vectorized", "copy_file"}:
        from depth_anything_3.streaming_task import pipeline

        return getattr(pipeline, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if __name__ == "__main__":
    main()
