"""Resolve training experiment paths and record each distributed execution."""

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from omegaconf import OmegaConf

from vggt.runtime_paths import execution_id, experiment_root, run_name


def configure_output(cfg, *, name=None, legacy=False):
    """Choose a purpose directory. Existing recipes can manage their own paths."""
    mode = cfg.get("mode", "train")
    if mode not in ("train", "val"):
        raise ValueError(f"Invalid training mode {mode!r}. Use 'train' or 'val' in the recipe.")

    if name is not None:
        name = run_name(name)
    if legacy:
        cfg.exp_name = name or "exp001"
        cfg.logging.log_dir = "logs"
        cfg.checkpoint.save_dir = "logs/${exp_name}/ckpts"
        return None
    if name is not None:
        cfg.exp_name = name
    if "experiment_dir" not in cfg:
        return None

    phase = "val" if mode == "val" else "train"
    dataset_configs = cfg.data[phase].dataset.dataset_configs
    reader_names = {config._target_.split(".")[-1] for config in dataset_configs}
    dataset_name = {"Co3dDataset": "common_objects_3d", "VKittiDataset": "virtual_kitti_2"}
    dataset = dataset_name.get(next(iter(reader_names)), "training_sources") if len(reader_names) == 1 else "training_sources"
    output = experiment_root() / dataset / "geometry_transformer" / "fine_tune" / run_name(cfg.exp_name)
    if mode == "val":
        output /= "validation"
    cfg.experiment_dir = str(output)
    return output


class TrainingRun:
    """Give every attempt its own effective config, logs, and checkpoints."""

    def __init__(self, config, directory):
        self.config = config
        self.directory = directory
        self.manifest_path = None
        self.manifest = None

    def _manifests(self):
        manifests = [
            *self.directory.glob("executions/*/metadata/manifest.json"),
            *self.directory.glob("metadata/executions/*/manifest.json"),
        ]
        return sorted(
            manifests,
            key=lambda path: (
                path.parents[1].name if path.parent.name == "metadata" else path.parent.name
            ).replace(".", ""),
            reverse=True,
        )

    def read(self, run_id):
        """Locate one manifest without initializing the training runtime."""
        if run_id == "latest":
            manifest = next(iter(self._manifests()), None)
            if manifest is not None:
                return manifest
        elif re.fullmatch(r"[0-9]{8}T[0-9]{6}\.?[0-9]{6}Z-[0-9a-f]{12}", run_id):
            for manifest in (
                self.directory / "executions" / run_id / "metadata" / "manifest.json",
                self.directory / "metadata" / "executions" / run_id / "manifest.json",
            ):
                if manifest.is_file():
                    return manifest
        raise FileNotFoundError(f"No run manifest for {run_id!r} under {self.directory}")

    def _resume_checkpoint(self):
        for manifest in self._manifests():
            try:
                record = json.loads(manifest.read_text())
            except (OSError, ValueError) as error:
                logging.warning("Could not read run manifest %s: %s", manifest, error)
                continue
            checkpoint = record.get("checkpoint") if isinstance(record, dict) else None
            if not isinstance(checkpoint, str) or not checkpoint:
                continue
            path = self.directory / checkpoint
            if path.is_file():
                return str(path)
        return None

    def start(self, distributed, logging_config, checkpoint_config):
        """Assign an execution on rank zero and share writable paths with all ranks."""
        rank = distributed.get_rank()
        started_at = datetime.now(timezone.utc)
        managed_logs = logging_config.log_dir == str(self.directory / "logs")
        managed_checkpoints = checkpoint_config.save_dir == str(self.directory / "artifacts" / "checkpoints")
        resume = checkpoint_config.resume_checkpoint_path
        if rank == 0 and resume is None and managed_checkpoints:
            resume = self._resume_checkpoint()
        assignment = [execution_id(started_at), resume] if rank == 0 else [None, None]
        distributed.broadcast_object_list(assignment, src=0)
        run_id, resume = assignment

        run = self.directory / "executions" / run_id
        if managed_logs:
            logging_config.log_dir = str(run / "logs")
        if managed_checkpoints:
            checkpoint_config.save_dir = str(run / "artifacts" / "checkpoints")
        checkpoint_config.resume_checkpoint_path = resume
        if rank != 0:
            return

        metadata = run / "metadata"
        metadata.mkdir(parents=True)
        config_path = metadata / "config.yaml"
        role = "validation" if self.config.get("mode") == "val" else None
        study = self.directory.parent if role else self.directory
        component_paths = {
            "dataset": study.parents[2].name,
            "model": study.parents[1].name,
            "task": study.parent.name,
        }
        recorded_config = OmegaConf.merge(
            OmegaConf.to_container(self.config, resolve=True), {"component_paths": component_paths}
        )
        OmegaConf.save(recorded_config, config_path, resolve=True)
        self.manifest = {
            "id": run_id,
            "run_id": run_id,
            "subname": study.name,
            "role": role,
            "task": component_paths["task"],
            "effective_config": "metadata/config.yaml",
            "outputs": {},
            "started_at": started_at.isoformat(),
            "config": str(config_path.relative_to(self.directory)),
            "logs": self._result_path(logging_config.log_dir),
            "checkpoint": self._result_path(Path(checkpoint_config.save_dir) / "checkpoint.pt"),
            "resume_checkpoint": resume,
            "python": sys.executable,
            "world_size": distributed.get_world_size(),
        }
        self.manifest_path = metadata / "manifest.json"
        self.finish("running")
        print(f"Run manifest: {self.manifest_path}", flush=True)

    def _result_path(self, value):
        path = Path(value).absolute()
        return str(path.relative_to(self.directory)) if path.is_relative_to(self.directory) else str(path)

    def finish(self, status):
        """Publish status atomically for readers while other ranks leave it untouched."""
        if self.manifest_path is None:
            return
        self.manifest["status"] = "succeeded" if status == "completed" else status
        if status != "running":
            self.manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
            run = self.manifest_path.parents[1]
            outputs = {
                path.stem: path.relative_to(run).as_posix()
                for path in (run / "artifacts").rglob("*.pt")
            }
            if status == "completed":
                report = run / "reports" / "summary.json"
                report.parent.mkdir(exist_ok=True)
                report.write_text(json.dumps({
                    "mode": self.config.get("mode", "train"),
                    "checkpoint": self.manifest["checkpoint"],
                    "logs": self.manifest["logs"],
                }, indent=2) + "\n")
                outputs["summary"] = "reports/summary.json"
            self.manifest["outputs"] = outputs
        temporary = self.manifest_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.manifest, indent=2) + "\n")
        os.replace(temporary, self.manifest_path)
