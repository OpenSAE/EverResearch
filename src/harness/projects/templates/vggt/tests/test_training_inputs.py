"""Check dataset setup and checkpoint round trips with synthetic inputs."""

import gzip
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch


CONF = Path(__file__).resolve().parents[1] / "conf"


def test_co3d_rejects_an_empty_split(tmp_path, monkeypatch):
    pytest.importorskip("hydra")
    from hydra import compose, initialize_config_dir

    from vggt.co3d.dataset import Co3dDataset

    with initialize_config_dir(version_base=None, config_dir=str(CONF)):
        cfg = compose(config_name="config")

    common = cfg.data.train.common_config
    common.debug = True
    annotation_path = tmp_path / "apple_train.jgz"
    with gzip.open(annotation_path, "wt") as annotations:
        json.dump({"short": [{}]}, annotations)

    with pytest.raises(ValueError, match="No CO3D train sequences"):
        Co3dDataset(common, CO3D_DIR=tmp_path, CO3D_ANNOTATION_DIR=tmp_path, min_num_images=2)

    with gzip.open(annotation_path, "wt") as annotations:
        json.dump({"usable": [{}, {}]}, annotations)

    dataset = Co3dDataset(common, CO3D_DIR=tmp_path, CO3D_ANNOTATION_DIR=tmp_path, min_num_images=2)
    assert dataset.sequence_list == ["usable"]
    assert dataset.total_frame_num == 2


def test_virtual_kitti_discovers_camera_folders_on_read_only_inputs(tmp_path, monkeypatch):
    pytest.importorskip("hydra")
    from hydra import compose, initialize_config_dir

    from vggt.virtual_kitti.dataset import VKittiDataset

    with initialize_config_dir(version_base=None, config_dir=str(CONF)):
        cfg = compose(config_name="config")

    common = cfg.data.train.common_config
    with pytest.raises(ValueError, match="No Virtual KITTI 2 sequences found"):
        VKittiDataset(common, VKitti_DIR=tmp_path)
    entry = "Scene01/clone/frames/rgb/Camera_0"
    (tmp_path / entry).mkdir(parents=True)
    dataset = VKittiDataset(common, VKitti_DIR=tmp_path)
    assert dataset.sequence_list == [entry]
    index = tmp_path / "sequence_list.txt"
    assert not index.exists()
    index.write_text("\n" + entry + "\n")
    assert VKittiDataset(common, VKitti_DIR=tmp_path).sequence_list == [entry]
    test_entry = "Scene02/clone/frames/rgb/Camera_0"
    (tmp_path / "test_sequences.txt").write_text(test_entry + "\n")
    validation_data = VKittiDataset(
        common, split="test", VKitti_DIR=tmp_path, sequence_list_path="test_sequences.txt"
    )
    assert validation_data.sequence_list == [test_entry]
    with pytest.raises(FileNotFoundError, match="missing.txt"):
        VKittiDataset(common, VKitti_DIR=tmp_path, sequence_list_path="missing.txt")


def test_checkpoint_write_failure_preserves_previous_checkpoint(tmp_path, monkeypatch):
    pytest.importorskip("iopath")
    pytest.importorskip("wcmatch")
    from vggt.runtime.train_utils.checkpoint import robust_torch_save

    checkpoint = tmp_path / "checkpoint.pt"
    robust_torch_save({"step": 1}, str(checkpoint))
    with monkeypatch.context() as patch:
        def interrupted_write(value, destination):
            destination.write(b"partial checkpoint")
            raise OSError("synthetic write failure")

        patch.setattr(torch, "save", interrupted_write)
        with pytest.raises(OSError, match="synthetic write failure"):
            robust_torch_save({"step": 2}, str(checkpoint))

    assert list(tmp_path.iterdir()) == [checkpoint]
    assert torch.load(checkpoint) == {"step": 1}
    robust_torch_save({"step": 2}, str(checkpoint))
    assert torch.load(checkpoint) == {"step": 2}


@pytest.mark.parametrize(("mode", "expected_epoch"), [("train", 5), ("val", 4)])
def test_checkpoint_writer_can_resume_training_and_validation(tmp_path, monkeypatch, mode, expected_epoch):
    pytest.importorskip("iopath")
    pytest.importorskip("wcmatch")
    pytest.importorskip("hydra")
    from vggt.fine_tune.trainer import Trainer
    from vggt.runtime.train_utils.checkpoint import DDPCheckpointSaver

    source_model = torch.nn.Linear(2, 1)
    source_optimizer = torch.optim.AdamW(source_model.parameters(), lr=0.05)
    source_model(torch.ones(2)).sum().backward()
    source_optimizer.step()
    saver = DDPCheckpointSaver(tmp_path, checkpoint_names=["checkpoint"], rank=0, epoch=4)
    saver.save_checkpoint(
        source_model,
        optimizer=source_optimizer.state_dict(),
        prev_epoch=4,
        steps={"train": 13, "val": 3},
        time_elapsed=19.0,
    )

    trainer = Trainer.__new__(Trainer)
    trainer.rank = 0
    trainer.mode = mode
    trainer.epoch = 0
    trainer.model = torch.nn.Linear(2, 1)
    trainer.checkpoint_conf = SimpleNamespace(strict=True)
    trainer.optim_conf = SimpleNamespace(amp=SimpleNamespace(enabled=False))
    if mode == "train":
        optimizer = torch.optim.AdamW(trainer.model.parameters(), lr=0.001)
        trainer.optims = [SimpleNamespace(optimizer=optimizer)]

    trainer._load_resuming_checkpoint(str(tmp_path / "checkpoint.pt"))

    assert trainer.epoch == expected_epoch
    assert trainer.steps == {"train": 13, "val": 3}
    assert trainer.ckpt_time_elapsed == 19.0
    torch.testing.assert_close(trainer.model.state_dict(), source_model.state_dict())
    if mode == "train":
        torch.testing.assert_close(optimizer.state_dict(), source_optimizer.state_dict())
