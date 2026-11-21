"""Check configuration, prediction handoff, and result readback without real weights."""

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from sam2.build_sam import compose_sam2_model_config
from sam2.tasks import image_inference


def test_installed_config_paths_cover_supported_models_and_legacy_names():
    project = Path(__file__).resolve().parents[1]
    reference = (project / "doc" / "conf.md").read_text()
    configured = {config for config, _ in image_inference.MODELS.values()}
    from sam2.config import load_config

    source_files = set(load_config("models/segment_anything/config.yaml"))
    assert configured == source_files
    for config in sorted(configured):
        assert config in reference
        model = compose_sam2_model_config(config).model
        assert model._target_ == "sam2.modeling.sam2_base.SAM2Base"
        if config.startswith("configs/sam2/"):
            assert compose_sam2_model_config(Path(config).name).model == model


def test_default_model_preview_does_not_write_or_build(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    image_inference.main(["--print-config", "--dataset", "example_images"])
    settings = json.loads(capsys.readouterr().out)
    assert settings["model"] == "sam2.1-hiera-large"
    assert settings["config"] == "configs/sam2.1/sam2.1_hiera_l.yaml"
    project = Path(__file__).resolve().parents[1]
    assert settings["checkpoint"] == str(
        (project / "data" / "checkpoints" / "local" / "sam2.1_hiera_large.pt").resolve()
    )
    assert Path(settings["experiment_dir"]).is_relative_to(project / "experiment")
    assert settings["model_config"]["_target_"] == "sam2.modeling.sam2_base.SAM2Base"
    assert settings["model_config"]["sam_mask_decoder_extra_args"][
        "dynamic_multimask_via_stability"
    ]
    assert settings["multimask_output"]
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("name", ["20261120", "002", "run", "trial_2", "other/path"])
def test_experiment_names_must_express_a_purpose(name, tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        image_inference.main(
            ["--print-config", "--name", name, "--experiment-root", str(tmp_path)]
        )
    assert exc.value.code == 2
    assert "one to three words" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_predict_and_read_result(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    image = tmp_path / "frame.png"
    Image.new("RGB", (9, 6)).save(image)
    checkpoint = tmp_path / "local.pt"
    checkpoint.touch()
    output_dir = tmp_path / "experiment"

    class Predictor:
        def set_image(self, image):
            assert image.size == (9, 6)
            assert image.mode == "RGB"

        def predict(self, point_coords, point_labels, multimask_output):
            np.testing.assert_array_equal(point_coords, [[4, 2], [0, 0]])
            np.testing.assert_array_equal(point_labels, [1, 0])
            assert not multimask_output
            return (
                np.ones((1, 6, 9), dtype=bool),
                np.array([0.5], dtype=np.float32),
                np.zeros((1, 256, 256), dtype=np.float32),
            )

    def build(config, *, ckpt_path, device):
        assert config == "configs/sam2/sam2_hiera_t.yaml"
        assert ckpt_path == checkpoint
        assert device.type == "cpu"
        return Predictor()

    monkeypatch.setattr(image_inference, "build_sam2", build)
    monkeypatch.setattr(image_inference, "SAM2ImagePredictor", lambda model: model)
    args = [
        "--image",
        str(image),
        "--dataset",
        "synthetic_images",
        "--point",
        "4",
        "2",
        "1",
        "--point",
        "0",
        "0",
        "0",
        "--model",
        "sam2-hiera-tiny",
        "--checkpoint",
        str(checkpoint),
        "--device",
        "cpu",
        "--single-mask",
        "--name",
        "object_click",
        "--experiment-root",
        "experiment",
    ]
    image_inference.main(args)
    artifact_dir = (
        output_dir
        / "synthetic_images"
        / "sam2_hiera_tiny"
        / "image_segmentation"
        / "object_click"
        / "executions"
    )
    (first,) = artifact_dir.glob("*/artifacts/prediction.npz")
    assert capsys.readouterr().out.strip() == str(first)
    image_inference.main(args)
    (second,) = set(artifact_dir.glob("*/artifacts/prediction.npz")) - {first}
    assert capsys.readouterr().out.strip() == str(second)
    settings, masks, scores, logits = image_inference.read_result(first)
    assert settings["run_id"] == first.parents[1].name
    assert settings["image"] == str(image)
    np.testing.assert_array_equal(masks, np.ones((1, 6, 9), dtype=bool))
    np.testing.assert_array_equal(scores, [0.5])
    assert logits.shape == (1, 256, 256)
    image_inference.main(["--read-result", str(second)])
    summary = json.loads(capsys.readouterr().out)
    assert summary["mask_shape"] == [1, 6, 9]
    assert summary["scores"] == [0.5]
