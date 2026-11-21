"""Check experiment output, readback, and compatibility with synthetic inputs."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_training_runs_keep_config_and_restore_previous_checkpoint(tmp_path, monkeypatch):
    hydra = pytest.importorskip("hydra")
    from omegaconf import OmegaConf

    from vggt.runtime import run_records

    class RankZero:
        def get_rank(self):
            return 0

        def get_world_size(self):
            return 1

        def broadcast_object_list(self, assignment, src):
            assert assignment[0] and src == 0

    monkeypatch.setattr(run_records, "experiment_root", lambda: tmp_path)

    def start_run():
        with hydra.initialize_config_dir(version_base=None, config_dir=str(ROOT / "conf")):
            cfg = hydra.compose(config_name="config", overrides=["checkpoint.resume_checkpoint_path=null"])
        experiment = run_records.configure_output(cfg, name="depth_comparison")
        run = run_records.TrainingRun(cfg, experiment)
        run.start(RankZero(), cfg.logging, cfg.checkpoint)
        return run, cfg

    first, first_cfg = start_run()
    assert first_cfg.checkpoint.resume_checkpoint_path is None
    checkpoint = Path(first_cfg.checkpoint.save_dir) / "checkpoint.pt"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_bytes(b"synthetic checkpoint location")
    first.finish("completed")

    imported_manifest = first.directory / "metadata/executions/z_imported/manifest.json"
    imported_manifest.parent.mkdir(parents=True)
    imported_manifest.write_text('{"status": "failed"}')
    second, second_cfg = start_run()
    imported_manifest.unlink()
    second.finish("failed")
    assert second_cfg.checkpoint.resume_checkpoint_path == str(checkpoint)
    assert first_cfg.checkpoint.save_dir != second_cfg.checkpoint.save_dir

    first_manifest = json.loads(second.read(first.manifest["id"]).read_text())
    second_manifest = json.loads(second.read("latest").read_text())
    assert first_manifest["status"] == "succeeded"
    assert second_manifest["status"] == "failed"
    assert (second.directory / first_manifest["checkpoint"]).read_bytes() == checkpoint.read_bytes()
    effective = OmegaConf.load(second.directory / second_manifest["config"])
    assert effective.checkpoint.resume_checkpoint_path == str(checkpoint)
    assert effective.logging.tensorboard_writer.path == f"{effective.logging.log_dir}/tensorboard"


def test_training_cli_supports_legacy_output_and_rejects_invalid_names(tmp_path):
    pytest.importorskip("hydra")
    from omegaconf import OmegaConf

    command = [sys.executable, str(ROOT / "main.py"), "train", "--print-config"]
    legacy = subprocess.run(command + ["--legacy-output"], check=True, capture_output=True, text=True, cwd=tmp_path)
    cfg = OmegaConf.create(legacy.stdout)
    assert cfg.logging.log_dir == "logs"
    assert cfg.checkpoint.save_dir == "logs/exp001/ckpts"

    for name in ("20261120", "001", "exp001", "run", "../scene"):
        invalid = subprocess.run(command + ["--run-name", name], capture_output=True, text=True, cwd=tmp_path)
        assert invalid.returncode == 2
        assert "Invalid experiment name" in invalid.stderr
    assert not list(tmp_path.iterdir())


def test_colmap_records_every_export_and_keeps_legacy_sparse_layout(tmp_path, monkeypatch):
    from vggt.demos import colmap

    class Reconstruction:
        def write(self, directory):
            (Path(directory) / "cameras.bin").write_bytes(b"synthetic cameras")

    class PointCloud:
        def export(self, path):
            Path(path).write_text("ply\n")

    monkeypatch.setattr(colmap, "experiment_root", lambda: tmp_path / "experiment")
    scene = tmp_path / "Known scene"
    args = argparse.Namespace(scene_dir=str(scene), use_ba=False, legacy_layout=False, run_name=None)
    first = colmap.save_reconstruction(args, Reconstruction(), PointCloud(), ["frame.png"])
    second = colmap.save_reconstruction(args, Reconstruction(), PointCloud(), ["frame.png"])
    assert first != second
    from vggt.colmap.records import unpack_reconstruction

    experiment = tmp_path / "experiment/scene_images/geometry_transformer/reconstruction/feed_forward"
    manifests = sorted(experiment.glob("executions/*/metadata/manifest.json"))
    assert len(manifests) == 2
    assert {
        path.parents[1] / json.loads(path.read_text())["outputs"]["reconstruction"]
        for path in manifests
    } == {first, second}
    assert {
        json.loads(path.with_name("config.json").read_text())["input"] for path in manifests
    } == {str(scene / "images")}
    sparse = unpack_reconstruction(manifests[-1], tmp_path / "readback")
    assert (sparse / "cameras.bin").read_bytes() == b"synthetic cameras"
    assert (sparse / "points.ply").read_text() == "ply\n"
    assert not scene.exists()

    args.legacy_layout = True
    assert colmap.save_reconstruction(args, Reconstruction(), PointCloud(), ["frame.png"]) == scene / "sparse"


def test_colmap_rejects_mixed_image_sizes_for_shared_camera_before_loading_weights(tmp_path, monkeypatch):
    from PIL import Image

    from vggt.demos import colmap

    images = tmp_path / "images"
    images.mkdir()
    Image.new("RGB", (12, 8)).save(images / "wide.png")
    Image.new("RGB", (8, 12)).save(images / "tall.png")
    monkeypatch.setattr(colmap.torch.cuda, "is_available", lambda: False)

    def unexpected_model_load(device):
        pytest.fail("Shared-camera validation must run before loading weights")

    monkeypatch.setattr(colmap, "load_demo_model", unexpected_model_load)
    monkeypatch.setattr(sys, "argv", ["demo_colmap.py", "--scene_dir", str(tmp_path), "--use_ba", "--shared_camera"])
    with pytest.raises(ValueError, match="same original width and height"):
        colmap.main()
    assert sorted(tmp_path.iterdir()) == [images]


@pytest.mark.parametrize("reconstruction_resolution", [518, 1024])
def test_colmap_unpads_camera_and_observations_in_the_same_coordinate_system(reconstruction_resolution):
    pytest.importorskip("pycolmap")
    import numpy as np

    from vggt.demos.colmap import rename_colmap_recons_and_rescale_camera
    from vggt.dependency.np_to_pycolmap import batch_np_matrix_to_pycolmap_wo_track

    # The camera sees this point at pixel (220, 330) in the padded 706-pixel square.
    focal_length = 300
    xyz = np.array([[(220 - 353) / focal_length, (330 - 353) / focal_length, 1]])
    reconstruction_scale = reconstruction_resolution / 706
    intrinsic = np.array([[[focal_length, 0, 353], [0, focal_length, 353], [0, 0, 1]]], dtype=float)
    intrinsic[:, :2, :] *= reconstruction_scale
    reconstruction = batch_np_matrix_to_pycolmap_wo_track(
        xyz,
        np.array([[220 * reconstruction_scale, 330 * reconstruction_scale, 0]]),
        np.array([[0, 0, 0]], dtype=np.uint8),
        np.eye(4)[None, :3, :],
        intrinsic,
        [reconstruction_resolution, reconstruction_resolution],
        camera_type="PINHOLE",
    )
    load_scale = 1024 / 706
    original_coords = np.array([[0, 88 * load_scale, 1024, (88 + 529) * load_scale, 706, 529]])
    rename_colmap_recons_and_rescale_camera(
        reconstruction,
        ["frame.png"],
        original_coords,
        reconstruction_resolution,
        shift_point2d_to_original_res=True,
        coordinates_resolution=1024,
    )

    camera = reconstruction.cameras[1]
    image = reconstruction.images[1]
    assert (camera.width, camera.height, image.name) == (706, 529, "frame.png")
    np.testing.assert_allclose(camera.params, [300, 300, 353, 265])
    np.testing.assert_allclose(image.points2D[0].xy, [220, 242])


def test_gradio_uploads_use_unique_workspaces(tmp_path, monkeypatch):
    pytest.importorskip("gradio")
    pytest.importorskip("trimesh")
    from vggt.demos import gradio_app

    monkeypatch.setattr(gradio_app, "project_root", lambda: tmp_path)
    gradio_app.upload_workspace.cache_clear()
    source = tmp_path / "input.png"
    source.write_bytes(b"synthetic upload")
    try:
        first, first_images = gradio_app.handle_uploads(None, [source])
        second, second_images = gradio_app.handle_uploads(None, [{"name": str(source)}])
        assert first != second
        assert Path(first).is_relative_to(tmp_path / "tmp/gradio_uploads")
        assert Path(first_images[0]).read_bytes() == source.read_bytes()
        assert Path(second_images[0]).read_bytes() == source.read_bytes()
    finally:
        gradio_app.upload_workspace.cache_clear()


def test_viewer_sky_masks_follow_frame_order_without_network(tmp_path, monkeypatch):
    pytest.importorskip("trimesh")
    import cv2
    import numpy as np

    from vggt.demos import visualization

    for name, pixel in (("first", 0), ("second", 255)):
        cv2.imwrite(str(tmp_path / f"{name}.png"), np.full((2, 2), pixel, dtype=np.uint8))

    confidence = np.ones((2, 2, 2), dtype=np.float32)
    frames = ["scene/second.png", "scene/first.png"]
    masked = visualization.mask_sky_confidence(confidence, frames, tmp_path)
    np.testing.assert_array_equal(masked[0], confidence[0])
    np.testing.assert_array_equal(masked[1], 0)
