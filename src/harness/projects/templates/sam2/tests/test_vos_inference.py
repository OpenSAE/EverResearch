"""Check the video command's frame ordering and sparse prompt masks."""

from types import SimpleNamespace

import numpy as np
import torch
from PIL import Image
from sam2.utils.misc import list_jpeg_frames
from sam2.video.inference import vos_inference


def test_all_masks_allows_sparse_per_object_annotations(tmp_path):
    frames = tmp_path / "images" / "clip"
    frames.mkdir(parents=True)
    for filename in ("10.jpeg", "2.JPG"):
        Image.new("RGB", (4, 3)).save(frames / filename)
    (frames / "frame_times.txt").touch()
    assert list_jpeg_frames(frames) == ["2.JPG", "10.jpeg"]
    annotations = tmp_path / "annotations"
    for object_id, frame in (("001", "2"), ("002", "2"), ("001", "10")):
        directory = annotations / "clip" / object_id
        directory.mkdir(parents=True, exist_ok=True)
        Image.new("L", (4, 3), 1).save(directory / f"{frame}.png")

    prompts = []
    scores = torch.ones((2, 1, 3, 4))
    predictor = SimpleNamespace(
        init_state=lambda **kwargs: {"video_height": 3, "video_width": 4},
        add_new_mask=lambda **kwargs: prompts.append(
            (kwargs["obj_id"], kwargs["frame_idx"])
        ),
        propagate_in_video=lambda state: iter(
            ((0, [1, 2], scores), (1, [1, 2], scores))
        ),
    )
    predictions = tmp_path / "predictions"
    vos_inference(
        predictor,
        frames.parent,
        annotations,
        predictions,
        "clip",
        use_all_masks=True,
        per_obj_png_file=True,
    )
    assert set(prompts) == {(1, 0), (2, 0), (1, 1)}
    assert len(prompts) == 3
    assert {
        path.relative_to(predictions).as_posix() for path in predictions.rglob("*.png")
    } == {
        "clip/001/2.png",
        "clip/001/10.png",
        "clip/002/2.png",
        "clip/002/10.png",
    }
    with Image.open(predictions / "clip" / "002" / "10.png") as mask:
        np.testing.assert_array_equal(np.asarray(mask), np.ones((3, 4), dtype=np.uint8))
