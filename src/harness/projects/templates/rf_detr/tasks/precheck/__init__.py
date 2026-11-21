# ------------------------------------------------------------------------
# RF-DETR
# Copyright (c) 2025 Roboflow. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 [see LICENSE for details]
# ------------------------------------------------------------------------
"""Check a selected RF-DETR CLI task against a bounded set of actual batches.

Lightning's fast development mode uses the same model, checkpoint and dataset
configuration with one batch per active phase. The named launcher also records
the precheck result in the execution manifest.
"""

import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
from typing import Any

import torch
from pytorch_lightning import Callback, LightningModule, Trainer

PRECHECK_COMPLETE = "RFDETR_CLI_PRECHECK_COMPLETE"


class PrecheckSampleCounter(Callback):
    """Count the actual images consumed by the bounded Lightning loops."""

    def __init__(self, count_file: str) -> None:
        self.count_file = Path(count_file)
        self.samples_checked = 0

    def on_train_batch_end(
        self, trainer: Trainer, pl_module: LightningModule, outputs: Any, batch: Any, batch_idx: int
    ) -> None:
        self.samples_checked += batch[0].tensors.shape[0]

    def on_validation_batch_end(
        self,
        trainer: Trainer,
        pl_module: LightningModule,
        outputs: Any,
        batch: Any,
        batch_idx: int,
        dataloader_idx: int = 0,
    ) -> None:
        self.samples_checked += batch[0].tensors.shape[0]

    def on_test_batch_end(
        self,
        trainer: Trainer,
        pl_module: LightningModule,
        outputs: Any,
        batch: Any,
        batch_idx: int,
        dataloader_idx: int = 0,
    ) -> None:
        """Count samples consumed by a test batch."""
        self.samples_checked += batch[0].tensors.shape[0]

    def on_predict_batch_end(
        self,
        trainer: Trainer,
        pl_module: LightningModule,
        outputs: Any,
        batch: Any,
        batch_idx: int,
        dataloader_idx: int = 0,
    ) -> None:
        """Count samples consumed by a prediction batch."""
        self.samples_checked += batch[0].tensors.shape[0]

    def on_fit_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        """Record the training and validation sample count."""
        self._write_count(trainer, pl_module)

    def on_validation_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        """Record samples when validation was the requested task."""
        self._write_count(trainer, pl_module)

    def on_test_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        """Record samples when testing was the requested task."""
        self._write_count(trainer, pl_module)

    def on_predict_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        """Record samples when prediction was the requested task."""
        self._write_count(trainer, pl_module)

    def _write_count(self, trainer: Trainer, pl_module: LightningModule) -> None:
        """Reduce the per-worker counts and record their total."""
        count = torch.tensor(self.samples_checked, device=pl_module.device)
        total = trainer.strategy.reduce(count, reduce_op="sum")
        if trainer.is_global_zero:
            self.count_file.write_text(str(int(total.item())), encoding="utf-8")


def check_fit(command: list[str]) -> dict[str, Any]:
    """Check a named training launch using the same task precheck as the CLI."""
    return check_task(command)


def check_task(command: list[str]) -> dict[str, Any]:
    """Return the outcome of an isolated, one-batch check per active phase."""
    started = monotonic()
    with TemporaryDirectory(prefix="rfdetr-precheck-") as temporary:
        output = Path(temporary)
        count_file = output / "sample_count"
        counter = {
            "class_path": "rfdetr.precheck.PrecheckSampleCounter",
            "init_args": {"count_file": str(count_file)},
        }
        bounded = [
            *command,
            "--trainer.fast_dev_run=1",
            "--trainer.logger=false",
            f"--trainer.callbacks+={json.dumps(counter)}",
            f"--model.train_config.init_args.output_dir={output}",
            f"--trainer.default_root_dir={output}",
        ]
        completed = subprocess.run(bounded, capture_output=True, text=True, check=False, env=checked_environment())
        samples_checked = int(count_file.read_text(encoding="utf-8")) if count_file.is_file() else None
    result = {
        "status": "failed" if completed.returncode else "passed",
        "returncode": completed.returncode,
        "duration_seconds": monotonic() - started,
        "samples_checked": samples_checked,
    }
    if completed.returncode:
        result["error"] = (completed.stderr or completed.stdout or "No diagnostic output.").strip()
    return result


def checked_environment() -> dict[str, str]:
    """Mark a child process that is performing or has passed preliminary validation."""
    return {**os.environ, PRECHECK_COMPLETE: "1"}
