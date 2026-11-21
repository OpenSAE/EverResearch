"""Check the standalone Hydra training launch without starting a training job."""

import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest
from hydra import initialize_config_module
from omegaconf import OmegaConf

pytest.importorskip("submitit")
pytest.importorskip("iopath")
from training import train

PROJECT = Path(__file__).resolve().parents[1]
RECIPE = "configs/sam2.1_training/sam2.1_hiera_b+_MOSE_finetune.yaml"


def test_local_training_preview_uses_effective_overrides(tmp_path):
    destination = tmp_path / "fine_tuning"
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT / "main.py"),
            "train",
            "-c",
            RECIPE,
            "--use-cluster",
            "0",
            "--num-gpus",
            "2",
            "--num-nodes",
            "3",
            "--experiment-log-dir",
            str(destination),
            "--print-config",
        ],
        cwd=PROJECT,
        check=True,
        capture_output=True,
        text=True,
    )
    config = OmegaConf.create(result.stdout)
    assert config.launcher.gpus_per_node == 2
    assert config.launcher.num_nodes == 1
    assert config.submitit.use_cluster is False
    assert config.trainer.checkpoint.save_dir == str(destination / "checkpoints")
    assert not destination.exists()


def test_training_saves_the_config_used_by_the_launcher(monkeypatch, tmp_path):
    from hydra.core.global_hydra import GlobalHydra

    if not GlobalHydra.instance().is_initialized():
        initialize_config_module("sam2", version_base="1.2")
    train.register_omegaconf_resolvers()
    launched = []
    monkeypatch.setattr(
        train, "single_node_runner", lambda cfg, port: launched.append(cfg)
    )
    train.main(
        Namespace(
            config=RECIPE,
            num_gpus=3,
            num_nodes=4,
            use_cluster=False,
            partition=None,
            account=None,
            qos=None,
            experiment_log_dir=str(tmp_path),
        )
    )
    saved = OmegaConf.load(tmp_path / "config_resolved.yaml")
    assert len(launched) == 1
    assert OmegaConf.to_container(saved) == OmegaConf.to_container(
        launched[0], resolve=True
    )
    assert saved.launcher.gpus_per_node == 3
    assert saved.launcher.num_nodes == 1
