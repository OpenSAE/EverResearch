"""Regression checks for input selection, named runs, and prediction readback."""

import json

import numpy as np
import pytest
from PIL import Image
from typer.testing import CliRunner

from depth_anything_3 import cli
from depth_anything_3.registry import MODEL_REGISTRY
from depth_anything_3.services.inference_service import InferenceService
from depth_anything_3.specs import Prediction
from depth_anything_3.utils.export import export
from depth_anything_3.utils.export.npz import read_depth


runner = CliRunner()


def test_published_model_presets_load_together():
    assert set(MODEL_REGISTRY) == {
        "da3-base", "da3-giant", "da3-large", "da3-small",
        "da3metric-large", "da3mono-large", "da3nested-giant-large",
    }


def test_invalid_resolution_is_recorded_before_model_load(tmp_path, monkeypatch):
    image = tmp_path / "sample.png"
    image.touch()
    destination = tmp_path / "experiment"
    monkeypatch.setattr(cli, "experiment_directory", lambda *_: destination)

    def unexpected_model_load(self):
        pytest.fail("An invalid resolution must be rejected before loading weights")

    monkeypatch.setattr(InferenceService, "load_model", unexpected_model_load)
    result = runner.invoke(cli.app, [
        "auto", str(image), "--experiment", "scene_geometry", "--process-res", "0",
    ])
    assert result.exit_code == 1
    record = json.loads(next(destination.glob("executions/*/manifest.json")).read_text())
    assert record["status"] == "failed"
    assert record["formal_started"] is False
    assert record["diagnostics"] == [{
        "stage": "automatic_precheck", "message": "Processing resolution must be positive"
    }]


def test_preview_resolves_default_and_overrides(tmp_path, monkeypatch):
    image = tmp_path / "sample.png"
    image.touch()
    destination = tmp_path / "unused"
    monkeypatch.setattr(cli, "experiment_directory", lambda *_: destination)
    result = runner.invoke(cli.app, [
        "auto", str(image), "--experiment", "scene_geometry", "--show-config",
        "--process-res", "56", "--device", "cpu",
    ])
    assert result.exit_code == 0, result.output
    settings = json.loads(result.output)
    assert settings["model_dir"] == "depth-anything/DA3NESTED-GIANT-LARGE-1.1"
    assert settings["input_type"] == "image"
    assert settings["process_res"] == 56
    assert settings["device"] == "cpu"
    assert settings["output_root"] == str(destination)
    assert not destination.exists()


@pytest.mark.parametrize("name", ["20261120", "3", "run", "run_2", "a/b"])
def test_experiment_name_is_checked_before_writing(tmp_path, name):
    image = tmp_path / "sample.png"
    image.touch()
    result = runner.invoke(cli.app, ["auto", str(image), "--experiment", name, "--show-config"])
    assert result.exit_code == 2
    assert "scene_geometry" in result.output
    assert list(tmp_path.iterdir()) == [image]


@pytest.mark.parametrize("command", ["auto", "video"])
def test_video_rejects_invalid_fps_before_writing(tmp_path, command):
    video = tmp_path / "sample.mp4"
    video.touch()
    output = tmp_path / "output"
    result = runner.invoke(cli.app, [
        command, str(video), "--fps", "0", "--export-dir", str(output)
    ])
    assert result.exit_code == 2
    assert "finite positive" in result.output
    assert not output.exists()


@pytest.mark.parametrize(
    "command, source_kind",
    [("image", "image"), ("images", "directory"), ("colmap", "directory"), ("video", "video")],
)
def test_explicit_input_commands_forward_reference_strategy(
    tmp_path, monkeypatch, command, source_kind
):
    image = tmp_path / "sample.png"
    Image.new("RGB", (4, 3)).save(image)
    video = tmp_path / "sample.mp4"
    sources = {"image": image, "directory": tmp_path, "video": video}
    monkeypatch.setattr(cli.ColmapHandler, "process", lambda *_: ([str(image)], None, None))
    monkeypatch.setattr(cli.VideoHandler, "process", lambda *_: [str(image)])
    predictions = []

    class Model:
        def inference(self, **options):
            predictions.append(options)

    monkeypatch.setattr(InferenceService, "load_model", lambda _: Model())
    result = runner.invoke(cli.app, [
        command, str(sources[source_kind]), "--export-dir", str(tmp_path / "output"),
        "--ref-view-strategy", "middle",
    ])
    assert result.exit_code == 0, result.exception or result.output
    assert len(predictions) == 1
    assert predictions[0]["image"] == [str(image)]
    assert predictions[0]["ref_view_strategy"] == "middle"


@pytest.mark.parametrize("export_format", ["npz", "mini_npz"])
def test_named_repeats_and_legacy_export_use_the_same_input_and_writer(tmp_path, monkeypatch, export_format):
    source = tmp_path / "scene"
    source.mkdir()
    for name in ("b.PnG", "a.webp"):
        Image.new("RGB", (4, 3), color="black").save(source / name)
    (source / "folder.png").mkdir()
    destination = tmp_path / "experiment"
    monkeypatch.setattr(cli, "experiment_directory", lambda *_: destination)
    depth = np.arange(24, dtype=np.float32).reshape(2, 3, 4)
    expected_inputs = [str(source / "a.webp"), str(source / "b.PnG")]

    def fake_inference(*, image_paths, export_format, export_dir, **options):
        assert image_paths == expected_inputs
        assert options["model_dir"] == "depth-anything/DA3NESTED-GIANT-LARGE-1.1"
        processed_images = np.zeros((2, 3, 4, 3), dtype=np.uint8)
        export(Prediction(depth, is_metric=0, processed_images=processed_images), export_format, export_dir)

    monkeypatch.setattr(cli, "run_inference", fake_inference)
    arguments = ["auto", str(source), "--export-format", export_format]
    for _ in range(2):
        result = runner.invoke(cli.app, [*arguments, "--experiment", "scene_geometry"])
        assert result.exit_code == 0, result.output

    result = runner.invoke(cli.app, ["results", str(destination)])
    assert result.exit_code == 0, result.output
    records = json.loads(result.output)
    assert len(records) == 2
    assert [record["execution_id"] for record in records] == ["inference_execution_one", "inference_execution_two"]
    assert len({record["run_id"] for record in records}) == 2
    for record in records:
        assert record["status"] == "succeeded"
        execution = destination / "executions" / record["execution_id"]
        settings = json.loads((execution / record["config"]).read_text())
        assert settings["input_path"] == str(source)
        assert settings["export_format"] == export_format
        recorded_format = "numpy_archive" if export_format == "npz" else export_format
        assert record["artifacts"] == [f"artifacts/exports/{recorded_format}/results.npz"]
        np.testing.assert_array_equal(read_depth(execution / "artifacts", export_format), depth)

    legacy_output = tmp_path / "old_output"
    result = runner.invoke(cli.app, [*arguments, "--export-dir", str(legacy_output)])
    assert result.exit_code == 0, result.output
    assert (legacy_output / "exports" / export_format / "results.npz").is_file()
    np.testing.assert_array_equal(read_depth(legacy_output, export_format), depth)


def test_export_failure_is_recorded_by_cli(tmp_path, monkeypatch):
    image = tmp_path / "sample.png"
    image.touch()
    destination = tmp_path / "experiment"
    monkeypatch.setattr(cli, "experiment_directory", lambda *_: destination)

    def failed_export(*, image_paths, export_format, export_dir, **options):
        export(Prediction(np.ones((1, 2, 2)), is_metric=0), export_format, export_dir)

    monkeypatch.setattr(cli, "run_inference", failed_export)
    result = runner.invoke(cli.app, [
        "auto", str(image), "--experiment", "scene_geometry", "--export-format", "npz",
    ])
    assert result.exit_code == 1
    assert "processed_images is required" in str(result.exception)
    record = json.loads(next(destination.glob("executions/*/manifest.json")).read_text())
    assert record["status"] == "failed"
    assert record["artifacts"] == []
