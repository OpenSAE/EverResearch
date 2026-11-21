# ------------------------------------------------------------------------
# RF-DETR
# Copyright (c) 2025 Roboflow. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 [see LICENSE for details]
# ------------------------------------------------------------------------
"""Exercise the checkout's training experiment paths and execution records."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import train_experiment


@pytest.fixture
def fit_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[str]:
    """Select a named COCO experiment and isolate its output tree."""
    monkeypatch.setattr(train_experiment, "PROJECT_ROOT", tmp_path)
    return ["fit", "--dataset", "coco", "--name", "default_finetuning"]


@pytest.fixture
def training_process(mocker: Any) -> Any:
    """Use a parsed Lightning configuration and a small stand-in for training artifacts."""
    configuration = """\
trainer:
  default_root_dir: null
model:
  model_config:
    class_path: rfdetr.config.RFDETRNanoConfig
  train_config:
    init_args:
      dataset_dir: /data/coco
      dataset_file: coco
      output_dir: output/rfdetr_nano
"""

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if command[-1] == "--print_config":
            return subprocess.CompletedProcess(command, 0, stdout=configuration)
        option = next(arg for arg in command if arg.startswith("--model.train_config.init_args.output_dir="))
        output = Path(option.partition("=")[2])
        (output / "metrics.csv").write_text("epoch,val/mAP_50_95\n0,0.0\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    return mocker.patch.object(train_experiment.subprocess, "run", side_effect=run)


class TestTrainExperiment:
    def test_plan_is_read_only(
        self, fit_command: list[str], training_process: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert train_experiment.main([*fit_command, "--plan", "--", "--trainer.accelerator=cpu"]) == 0

        training_process.assert_called_once()
        assert training_process.call_args.args[0][-2:] == ["--trainer.accelerator=cpu", "--print_config"]
        plan = json.loads(capsys.readouterr().out)
        assert (
            Path(plan["experiment_directory"])
            == tmp_path / "experiment/coco/rfdetr_detection_nano/train/default_finetuning"
        )
        assert plan["fit_configuration"]["model"]["train_config"]["init_args"]["dataset_file"] == "coco"
        assert not (tmp_path / "experiment").exists()

    @pytest.mark.parametrize("name", ["run", "20261120", "1", "run_1", "control/variant"])
    def test_invalid_names_fail_before_any_write(
        self, name: str, fit_command: list[str], tmp_path: Path, training_process: Any
    ) -> None:
        with pytest.raises(SystemExit, match="2"):
            train_experiment.main([*fit_command[:-1], name])

        training_process.assert_not_called()
        assert not (tmp_path / "experiment").exists()

    def test_repeat_execution_keeps_results(
        self, fit_command: list[str], training_process: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        for _ in range(2):
            assert train_experiment.main(fit_command) == 0

        experiment = tmp_path / "experiment/coco/rfdetr_detection_nano/train/default_finetuning"
        capsys.readouterr()
        assert train_experiment.main(["results", str(experiment)]) == 0
        results = json.loads(capsys.readouterr().out)
        assert len({result["execution_id"] for result in results}) == 2
        for result in results:
            directory = Path(result["directory"])
            assert result["status"] == "completed"
            assert result["artifacts"] == ["metrics.csv"]
            assert result["fit_configuration"]["trainer"]["default_root_dir"] == str(directory)
            assert (directory / "metrics.csv").read_text(encoding="utf-8").endswith("0,0.0\n")

    def test_child_failure_is_recorded(self, fit_command: list[str], training_process: Any, tmp_path: Path) -> None:
        run = training_process.side_effect

        def fail_fit(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
            if command[-1] == "--print_config" or "--trainer.fast_dev_run=1" in command:
                return run(command, **kwargs)
            return subprocess.CompletedProcess(command, 4)

        training_process.side_effect = fail_fit
        assert train_experiment.main(fit_command) == 4

        (path,) = (tmp_path / "experiment").rglob(train_experiment.RECORD_NAME)
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["status"] == "failed"
        assert result["returncode"] == 4

    def test_precheck_report_alone_does_not_complete_training(
        self, fit_command: list[str], training_process: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run = training_process.side_effect

        def fit_without_artifacts(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
            if command[-1] == "--print_config":
                return run(command, **kwargs)
            if "--trainer.fast_dev_run=1" in command:
                callback = next(arg for arg in command if arg.startswith("--trainer.callbacks+="))
                count_file = json.loads(callback.partition("=")[2])["init_args"]["count_file"]
                Path(count_file).write_text("2", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0)

        training_process.side_effect = fit_without_artifacts
        assert train_experiment.main(fit_command) == 0

        (manifest,) = (tmp_path / "experiment").rglob(train_experiment.RECORD_NAME)
        capsys.readouterr()
        assert train_experiment.main(["results", str(manifest.parent)]) == 0
        (result,) = json.loads(capsys.readouterr().out)
        assert result["status"] == "stopped"
        assert result["artifacts"] == []
        assert result["outputs"] == {"precheck": "reports/precheck.json"}

    def test_failed_precheck_stops_before_formal_fit(
        self, fit_command: list[str], training_process: Any, tmp_path: Path
    ) -> None:
        run = training_process.side_effect

        def fail_precheck(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
            if "--trainer.fast_dev_run=1" in command:
                return subprocess.CompletedProcess(command, 5, stderr="Dataset shard cannot be opened.")
            return run(command, **kwargs)

        training_process.side_effect = fail_precheck
        assert train_experiment.main(fit_command) == 5
        assert training_process.call_count == 2
        (manifest,) = (tmp_path / "experiment").rglob(train_experiment.RECORD_NAME)
        result = json.loads(manifest.read_text(encoding="utf-8"))
        assert result["precheck"]["status"] == "failed"
        assert "Dataset shard cannot be opened" in result["precheck"]["error"]
        assert not list((tmp_path / "experiment").rglob("metrics.csv"))
