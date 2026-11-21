"""Verify lightweight commands and the viewer's CPU inference adapter."""

import subprocess
import sys
from pathlib import Path

import pytest
import torch

from vggt.demos import viser_app


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("script", "option"),
    [
        ("train", "--config"),
        ("colmap", "--scene_dir"),
        ("viser", "--image_folder"),
    ],
)
def test_command_help(script, option):
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), script, "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert option in result.stdout


def test_print_config_does_not_create_run_files(tmp_path):
    pytest.importorskip("hydra")
    from omegaconf import OmegaConf

    launcher = ROOT / "main.py"
    result = subprocess.run(
        [sys.executable, str(launcher), "train", "--config", "default.yaml", "--print-config"],
        check=True,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    cfg = OmegaConf.create(result.stdout)
    assert cfg.data.train.common_config.img_size == 518
    assert cfg.data.train.dataset.dataset_configs[0].split == "train"
    assert cfg.data.val.dataset.dataset_configs[0].split == "test"
    assert cfg.model.enable_depth and not cfg.model.enable_track
    expected = ROOT / "experiment/common_objects_3d/geometry_transformer/fine_tune/camera_depth"
    assert cfg.logging.log_dir == str(expected / "logs")
    assert cfg.checkpoint.save_dir == str(expected / "artifacts/checkpoints")
    assert not list(tmp_path.iterdir())


def test_viewer_uses_cpu_images_and_keeps_frame_order(monkeypatch):
    def unexpected_cuda_query(*args, **kwargs):
        pytest.fail("CPU inference queried CUDA compute capability")

    class SyntheticModel:
        def __call__(self, images):
            encoded_pose = torch.tensor([0, 0, 0, 0, 0, 0, 1, 1, 1], dtype=torch.float32)
            return {"pose_enc": encoded_pose.expand(1, len(images), -1), "images": images[None]}

    paths = ["scene/second.png", "scene/first.png"]
    monkeypatch.setattr(sys, "argv", ["demo_viser.py", "--image_folder", "scene", "--mask_sky"])
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.cuda, "get_device_capability", unexpected_cuda_query)
    monkeypatch.setattr(viser_app.glob, "glob", lambda pattern: paths)
    monkeypatch.setattr(viser_app, "load_demo_model", lambda device: SyntheticModel())

    def preprocess(image_paths):
        assert image_paths == paths
        return torch.ones(2, 3, 14, 28)

    def show(predictions, *, image_paths, mask_sky, **kwargs):
        assert predictions["intrinsic"].shape == (2, 3, 3)
        assert predictions["extrinsic"].shape == (2, 3, 4)
        assert predictions["images"].shape == (2, 3, 14, 28)
        assert image_paths == paths
        assert mask_sky

    monkeypatch.setattr(viser_app, "check_images", lambda paths: None)
    monkeypatch.setattr(viser_app, "load_and_preprocess_images", preprocess)
    monkeypatch.setattr(viser_app, "viser_wrapper", show)
    viser_app.main()


def test_trackers_share_positional_embeddings():
    from vggt.dependency.track_modules import utils as vggsfm
    from vggt.heads.track_modules import utils as vggt
    from vggt.utils import track_embedding

    assert vggt.get_2d_sincos_pos_embed is vggsfm.get_2d_sincos_pos_embed
    assert vggt.get_2d_embedding is track_embedding.get_2d_embedding
    assert vggt.get_2d_sincos_pos_embed(8, (2, 3)).shape == (1, 8, 2, 3)
    assert vggt.bilinear_sampler is not vggsfm.bilinear_sampler


def test_trackers_share_layers_and_keep_checkpoint_key_shapes():
    from vggt.dependency.track_modules import modules as vggsfm
    from vggt.heads.track_modules import modules as vggt
    from vggt.layers.tracking import attention

    assert vggt.Mlp is vggsfm.Mlp
    assert vggt.ResidualBlock is vggsfm.ResidualBlock
    sample = torch.randn(1, 2, 8)
    for layer, epsilon, affine in (
        (vggt.AttnBlock(8, 2), 1e-5, True),
        (vggsfm.AttnBlock(8, 2), 1e-6, False),
    ):
        assert layer(sample).shape == sample.shape
        assert layer.state_dict()["mlp.fc1.weight"].shape == (32, 8)
        assert layer.norm1.eps == epsilon
        assert ("norm1.weight" in layer.state_dict()) == affine

    context = torch.randn(1, 3, 8)
    mask = torch.tensor([[False, True, False], [True, False, False]])
    for layer, affine in ((vggt.CrossAttnBlock(8, 8, 2), True), (vggsfm.CrossAttnBlock(8, 8, 2), False)):
        assert isinstance(layer, attention.CrossAttnBlock)
        assert layer(sample, context, mask).shape == sample.shape
        assert ("norm1.weight" in layer.state_dict()) == affine
        assert "norm_context.weight" in layer.state_dict()
