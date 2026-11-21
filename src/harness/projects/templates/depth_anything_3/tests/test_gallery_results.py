"""Check gallery readback of direct exports and recorded experiment previews."""

from urllib.parse import unquote
from zipfile import ZipFile

from depth_anything_3.services.gallery import (
    build_group_list,
    build_group_manifest,
    read_bundled_preview,
)


def test_gallery_lists_direct_and_recorded_scenes(tmp_path):
    direct = tmp_path / "direct/scene"
    recorded = tmp_path / "execution/artifacts"
    for scene in (direct, recorded):
        (scene / "depth_vis").mkdir(parents=True)
        (scene / "scene.glb").touch()
    (direct / "scene.jpg").touch()
    (direct / "depth_vis/0000.jpg").write_bytes(b"direct")
    (recorded / "scene_preview.jpg").touch()
    with ZipFile(recorded / "frame_previews.zip", "w") as archive:
        archive.writestr("depth_vis/0000.jpg", b"first frame")
        archive.writestr("depth_vis/0001.jpg", b"second frame")

    assert [group["id"] for group in build_group_list(str(tmp_path))["groups"]] == [
        "direct", "execution",
    ]
    legacy, = build_group_manifest(str(tmp_path), "direct")["items"]
    assert legacy["thumbnail"] == "/direct/scene/scene.jpg"
    assert legacy["depth_images"] == ["/direct/scene/depth_vis/0000.jpg"]

    current, = build_group_manifest(str(tmp_path), "execution", url_prefix="/gallery")["items"]
    assert current["thumbnail"] == "/gallery/execution/artifacts/scene_preview.jpg"
    assert len(current["depth_images"]) == 2
    assert [read_bundled_preview(str(tmp_path), unquote(url.removeprefix("/gallery")))
            for url in current["depth_images"]] == [
        (b"first frame", "image/jpeg"), (b"second frame", "image/jpeg"),
    ]
