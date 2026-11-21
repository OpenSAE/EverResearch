# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Train model with configurable YAML file")
    parser.add_argument(
        "--config", 
        type=str, 
        default="default",
        help="Name of the config file (without .yaml extension, default: default)"
    )
    parser.add_argument(
        "--print-config",
        action="store_true",
        help="Print the resolved training configuration and exit",
    )
    parser.add_argument("--run-name", help="Name describing the purpose of the experiment")
    parser.add_argument("--show-run", metavar="ID", help="Read a run manifest by ID or use 'latest'")
    parser.add_argument("--legacy-output", action="store_true", help="Use the original logs and checkpoint layout")
    args = parser.parse_args()

    from hydra import compose, initialize_config_dir
    from omegaconf import OmegaConf, open_dict

    from vggt.runtime_paths import project_root
    from .run_records import TrainingRun, configure_output

    root = project_root()
    config_dir = root / "conf" if root is not None else Path(__file__).resolve().parents[1] / "configuration"
    config_name = args.config
    if config_name in {"default", "default.yaml"}:
        config_name = "config"
    path = Path(config_name)
    if path.is_absolute():
        config_dir, config_name = path.parent, path.name
    with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
        cfg = compose(config_name=config_name)
    if "catalogs" in cfg:
        with open_dict(cfg):
            del cfg["catalogs"]

    # Previously published recipes referred to the training script's import path.
    aliases = {
        "data.datasets.co3d.": "vggt.co3d.dataset.",
        "data.datasets.vkitti.": "vggt.virtual_kitti.dataset.",
        "data.": "vggt.scene_data.",
        "train_utils.": "vggt.runtime.train_utils.",
        "loss.": "vggt.fine_tune.loss.",
    }
    from omegaconf import DictConfig, ListConfig

    def update_targets(node):
        if isinstance(node, DictConfig) and "_target_" in node:
            target = node["_target_"]
            for old, new in aliases.items():
                if isinstance(target, str) and target.startswith(old):
                    node["_target_"] = new + target[len(old):]
                    break
        if isinstance(node, (DictConfig, ListConfig)):
            children = node.values() if isinstance(node, DictConfig) else node
            for child in children:
                update_targets(child)

    update_targets(cfg)

    try:
        run_directory = configure_output(cfg, name=args.run_name, legacy=args.legacy_output)
        run = TrainingRun(cfg, run_directory) if run_directory is not None else None
        if args.show_run:
            if run is None:
                parser.error("This recipe uses explicit or legacy paths and has no experiment manifest")
            print(run.read(args.show_run).read_text(), end="")
            return
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))

    if args.print_config:
        print(OmegaConf.to_yaml(cfg, resolve=True), end="")
        return

    from vggt.precheck.gate import check_training

    try:
        check_training(cfg)
    except ValueError as error:
        parser.error(str(error))

    from vggt.fine_tune.trainer import Trainer

    try:
        trainer = Trainer(**cfg, run_record=run)
        trainer.run()
    except KeyboardInterrupt:
        if run is not None:
            run.finish("interrupted")
        raise
    except Exception:
        if run is not None:
            run.finish("failed")
        raise
    else:
        if run is not None:
            run.finish("completed")


if __name__ == "__main__":
    main()


