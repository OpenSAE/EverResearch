"""目的和主要功能：检查传输与解压的实际文件结果、完成状态和可选文件摘要。

适用范围：使用合成压缩包与本地 rclone 连接，覆盖直接调用和已有项目调用。
"""

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

import pytest

from harness.utils.transfer import b2
from harness.utils.transfer.archive import Engine as ArchiveEngine


def make_tar(tmp_path, *, suffix=".tar", entries=None):
    source = tmp_path / ("source" + (".tar" if suffix == ".tar.zst" else suffix))
    if entries is None:
        entries = [
            ("data/chosen/a.h5ad", b"gene data"),
            ("data/chosen/cache/skip.bin", b"cache"),
            ("data/other/b", b"unrelated"),
        ]
    mode = {
        ".tar": "w",
        ".tar.zst": "w",
        ".tar.gz": "w:gz",
        ".tar.bz2": "w:bz2",
        ".tar.xz": "w:xz",
    }[suffix]
    with tarfile.open(source, mode) as stream:
        for name, data in entries:
            member = tarfile.TarInfo(name)
            if isinstance(data, tarfile.TarInfo):
                stream.addfile(data)
            else:
                member.size = len(data)
                stream.addfile(member, io.BytesIO(data))
    if suffix == ".tar.zst":
        if not shutil.which("zstd"):
            pytest.skip("zstd CLI is optional")
        output = tmp_path / "source.tar.zst"
        subprocess.run(["zstd", "-q", "-f", str(source), "-o", str(output)], check=True)
        source = output
    return source


@pytest.mark.parametrize("suffix", [".tar", ".tar.gz", ".tar.bz2", ".tar.xz", ".tar.zst"])
def test_selective_extract_preserves_only_selected_files(tmp_path, suffix):
    archive = make_tar(tmp_path, suffix=suffix)
    target = tmp_path / "restore"
    result = ArchiveEngine().extract(
        str(archive),
        str(target),
        include=("data/chosen",),
        exclude=("data/chosen/cache",),
        strip_components=2,
        execute=True,
        progress_interval=0,
    )
    assert result["status"] == "PASS"
    assert (target / "a.h5ad").read_bytes() == b"gene data"
    assert [p.name for p in target.iterdir()] == ["a.h5ad"]
    assert "sha256" not in result["files"][0]
    assert not list(tmp_path.glob(".restore.extract-*"))


def test_preview_does_not_read_payload_or_make_destination(tmp_path, monkeypatch):
    engine = ArchiveEngine()
    source = make_tar(tmp_path)
    import harness.utils.transfer.archive as module

    monkeypatch.setattr(module, "_stream", lambda *a: pytest.fail("preview read the payload"))
    target = tmp_path / "new" / "restore"
    result = engine.extract(str(source), str(target), include=("data/chosen",))
    assert result["status"] == "NOT_RUN" and result["mode"] == "preview"
    assert not target.parent.exists()


def test_listing_globs_case_and_single_file(tmp_path):
    source = make_tar(tmp_path)
    result = ArchiveEngine().extract(
        str(source),
        None,
        include=("DATA/CHOSEN/*.H5AD",),
        ignore_case=True,
        list_only=True,
        execute=True,
        progress_interval=0,
    )
    assert result["files"] == [{"path": "data/chosen/a.h5ad", "bytes": 9}]
    assert result["selected_bytes"] == 9
    assert not list(tmp_path.glob(".*.extract-*"))


@pytest.mark.parametrize(
    "name",
    ["../outside", "/absolute", "data/chosen/../outside", "C:/outside", "data\\chosen\\outside"],
)
def test_archive_paths_cannot_escape(tmp_path, name):
    archive = make_tar(tmp_path, entries=[(name, b"bad")])
    target = tmp_path / "restore"
    with pytest.raises(ValueError, match="path"):
        ArchiveEngine().extract(
            str(archive),
            str(target),
            include=("*",),
            execute=True,
            progress_interval=0,
        )
    assert not target.exists()
    assert not list(tmp_path.glob(".restore.extract-*"))


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE])
def test_links_and_special_files_are_rejected(tmp_path, kind):
    link = tarfile.TarInfo("data/chosen/link")
    link.type = kind
    link.linkname = "/outside"
    archive = make_tar(tmp_path, entries=[("data/chosen/good", b"ok"), (link.name, link)])
    target = tmp_path / "restore"
    with pytest.raises(ValueError, match="unsupported"):
        ArchiveEngine().extract(
            str(archive),
            str(target),
            include=("data/chosen",),
            strip_components=2,
            execute=True,
            progress_interval=0,
        )
    assert not target.exists() and not list(tmp_path.glob(".restore.extract-*"))


def test_existing_destination_and_missing_selection(tmp_path):
    engine = ArchiveEngine()
    source = make_tar(tmp_path)
    target = tmp_path / "restore"
    target.mkdir()
    marker = target / "existing"
    marker.write_text("keep")
    with pytest.raises(ValueError, match="new non-root"):
        engine.extract(str(source), str(target), include=("*",), execute=True)
    assert marker.read_text() == "keep"
    with pytest.raises(ValueError, match="No archive members"):
        engine.extract(
            str(source),
            str(tmp_path / "missing"),
            include=("absent",),
            execute=True,
            progress_interval=0,
        )
    assert not (tmp_path / "missing").exists()


def test_space_guard_and_optional_partial_preservation(tmp_path, monkeypatch):
    source = make_tar(tmp_path)
    import harness.utils.transfer.archive as module

    monkeypatch.setattr(
        module.shutil, "disk_usage", lambda p: shutil._ntuple_diskusage(100, 100, 0)
    )
    with pytest.raises(ValueError, match="Insufficient disk space"):
        ArchiveEngine().extract(
            str(source),
            str(tmp_path / "restore"),
            include=("data/chosen",),
            strip_components=2,
            execute=True,
            keep_partial=True,
            progress_interval=0,
        )
    assert not (tmp_path / "restore").exists()
    assert len(list(tmp_path.glob(".restore.extract-*"))) == 1


def test_truncated_zstd_never_publishes_partial_directory(tmp_path):
    source = make_tar(tmp_path, suffix=".tar.zst")
    source.write_bytes(source.read_bytes()[:-3])
    with pytest.raises((ValueError, tarfile.TarError)):
        ArchiveEngine().extract(
            str(source),
            str(tmp_path / "restore"),
            include=("data/chosen",),
            strip_components=2,
            execute=True,
            progress_interval=0,
        )
    assert not (tmp_path / "restore").exists()
    assert not list(tmp_path.glob(".restore.extract-*"))


@pytest.mark.parametrize("suffix", [".tar.gz", ".tar.bz2", ".tar.xz"])
def test_truncated_other_compression_never_publishes(tmp_path, suffix):
    source = make_tar(tmp_path, suffix=suffix)
    source.write_bytes(source.read_bytes()[:-3])
    with pytest.raises((OSError, EOFError, ValueError, tarfile.TarError)):
        ArchiveEngine().extract(
            str(source),
            str(tmp_path / "restore"),
            include=("data/chosen",),
            strip_components=2,
            execute=True,
            progress_interval=0,
        )
    assert not (tmp_path / "restore").exists()


def test_duplicate_output_is_not_overwritten(tmp_path):
    source = make_tar(tmp_path, entries=[("one/a", b"first"), ("two/a", b"second")])
    with pytest.raises(FileExistsError):
        ArchiveEngine().extract(
            str(source),
            str(tmp_path / "restore"),
            include=("*",),
            strip_components=1,
            execute=True,
            progress_interval=0,
        )
    assert not (tmp_path / "restore").exists()


def test_extraction_cli_receipt_and_failure_status(tmp_path):
    source = make_tar(tmp_path)
    engine = ArchiveEngine()
    receipt = tmp_path / "receipt.json"
    arguments = [
        "extract",
        "--archive",
        str(source),
        "--destination",
        str(tmp_path / "restore"),
        "--include",
        "data/chosen/a.h5ad",
        "--strip-components",
        "2",
        "--execute",
        "--receipt",
        str(receipt),
        "--progress-interval",
        "0",
    ]
    assert engine.main(argv=arguments) == 0
    saved = json.loads(receipt.read_text())
    assert saved["status"] == "PASS"
    assert saved["files"] == [{"path": "a.h5ad", "bytes": 9}]
    with pytest.raises(SystemExit):
        engine.main(argv=arguments)
    assert (
        engine.main(
            argv=[
                "list",
                "--archive",
                str(source),
                "--include",
                "absent",
                "--execute",
                "--progress-interval",
                "0",
            ]
        )
        == 1
    )


@pytest.mark.parametrize(
    "options",
    [
        {"strip_components": -1},
        {"reserve_gib": float("nan")},
        {"progress_interval": -1},
        {"include": ()},
    ],
)
def test_invalid_extraction_parameters(tmp_path, options):
    source = make_tar(tmp_path)
    keywords = {"include": ("*",), **options}
    with pytest.raises(ValueError):
        ArchiveEngine().extract(
            str(source),
            str(tmp_path / "restore"),
            **keywords,
        )


def test_download_filters_and_single_file_commands(tmp_path):
    engine = b2.Engine()
    command = engine.command(
        "pull",
        str(tmp_path / "dataset"),
        "b2:bucket/source",
        exclude=("/experiment/**",),
        include=("*.h5ad",),
    )
    assert command[:2] == ["rclone", "copy"]
    assert command[command.index("--exclude") + 1] == "/experiment/**"
    assert "--immutable" in command and "--dry-run" in command
    command = engine.command(
        "pull", str(tmp_path / "archive.tar.zst"), "b2:bucket/archive.tar.zst", single_file=True
    )
    assert command[:2] == ["rclone", "copyto"]
    local = tmp_path / "archive.tar.zst"
    local.write_text("data")
    command = engine.command("verify", str(local), "b2:bucket/archive.tar.zst", single_file=True)
    assert command[:4] == ["rclone", "check", str(local), "b2:bucket"]
    assert "--one-way" in command
    with pytest.raises(ValueError, match="matching"):
        engine.command("verify", str(local), "b2:bucket/renamed.zst", single_file=True)
    with pytest.raises(ValueError, match="duration"):
        engine.command("pull", str(tmp_path), "b2:bucket/source", timeout="--evil")


def test_preview_and_receipt_conflicts_never_start_rclone(tmp_path, monkeypatch):
    engine = b2.Engine()
    import harness.utils.transfer.b2 as module

    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("rclone executed"))
    arguments = ["pull", "--local", str(tmp_path / "restore"), "--remote", "b2:bucket/source"]
    assert engine.main(argv=arguments) == 0
    receipt = tmp_path / "existing.json"
    receipt.write_text("keep")
    with pytest.raises(SystemExit):
        engine.main(argv=arguments + ["--execute", "--receipt", str(receipt)])
    assert receipt.read_text() == "keep"


@pytest.mark.skipif(shutil.which("rclone") is None, reason="optional local rclone integration")
def test_file_download_and_verify_with_local_only_remote(tmp_path):
    source = tmp_path / "bucket" / "prefix"
    source.mkdir(parents=True)
    (source / "data.tar.zst").write_bytes(b"synthetic payload")
    config = tmp_path / "rclone.conf"
    config.write_text("[localtest]\ntype = local\n")
    environment = {**os.environ, "RCLONE_CONFIG": str(config)}
    destination = tmp_path / "downloaded" / "data.tar.zst"
    engine = b2.Engine()
    for action in ["pull", "verify"]:
        command = engine.command(
            action,
            str(destination),
            "localtest:bucket/prefix/data.tar.zst",
            single_file=True,
            execute=True,
        )
        result = subprocess.run(
            command, cwd=tmp_path, env=environment, capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == b"synthetic payload"


@pytest.mark.parametrize("sha256", [False, True])
def test_standalone_extraction_optional_digest(tmp_path, monkeypatch, sha256):
    from harness.utils.transfer import archive

    source = make_tar(tmp_path)
    if not sha256:
        monkeypatch.setattr(
            archive.hashlib, "sha256", lambda: pytest.fail("Unrequested digest computed")
        )
    target = tmp_path / "restore"
    result = ArchiveEngine().extract(
        str(source), str(target), include=("data/chosen/a.h5ad",),
        strip_components=2, execute=True, progress_interval=0, sha256=sha256,
    )
    assert result["project_id"] is None
    assert (target / "a.h5ad").read_bytes() == b"gene data"
    if sha256:
        assert result["files"][0]["sha256"] == hashlib.sha256(b"gene data").hexdigest()
    else:
        assert result["files"] == [{"path": "a.h5ad", "bytes": 9}]


def json_records(text):
    decoder = json.JSONDecoder()
    records = []
    while text.strip():
        record, end = decoder.raw_decode(text.lstrip())
        records.append(record)
        text = text.lstrip()[end:]
    return records


@pytest.mark.skipif(shutil.which("rclone") is None, reason="optional local rclone integration")
@pytest.mark.parametrize("folder", ["My Dataset", "科研 数据"])
def test_direct_module_transfer_completion_and_failure(tmp_path, folder):
    source = tmp_path / "input.txt"
    source.write_bytes(b"synthetic original")
    config = tmp_path / "rclone.conf"
    config.write_text("[localtest]\ntype = local\n")
    env = {**os.environ, "RCLONE_CONFIG": str(config)}
    remote = "localtest:" + str(tmp_path / "bucket" / folder / "sample.txt").lstrip("/")
    # The local backend resolves this relative remote path from filesystem root.
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
    base = [sys.executable, "-m", "harness.utils.transfer.b2"]
    receipt = tmp_path / "upload.json"
    def invoke(action, local, *extra):
        return subprocess.run(
            base + [action, "--file", "--local", str(local), "--remote", remote,
                    "--execute", "--retries", "1", "--low-level-retries", "1", *extra],
            cwd="/", env=env, text=True, capture_output=True,
        )
    pushed = invoke("push", source, "--receipt", str(receipt))
    assert pushed.returncode == 0, pushed.stderr
    completed = json_records(pushed.stdout)[-1]
    assert completed["status"] == "PASS" and completed["project_id"] is None
    assert completed == json.loads(receipt.read_text())
    assert completed["remote_integrity"] == "NOT_RUN"
    destination = tmp_path / "download.txt"
    pulled = invoke("pull", destination)
    assert pulled.returncode == 0, pulled.stderr
    assert destination.read_bytes() == b"synthetic original"
    assert json_records(pulled.stdout)[-1]["status"] == "PASS"
    repeated = invoke("push", source)
    assert repeated.returncode == 0, repeated.stderr
    assert json_records(repeated.stdout)[-1]["status"] == "PASS"
    source.write_bytes(b"different content with a different length")
    conflict = invoke("push", source)
    assert conflict.returncode != 0
    assert json_records(conflict.stdout)[-1]["status"] == "BLOCKED"
    diagnostic = json_records(conflict.stdout)[-1]["diagnostics"][0]
    assert diagnostic["code"] == "TARGET_CONFLICT"
    assert diagnostic["reason"] and diagnostic["impact"] and diagnostic["next_steps"]
    assert (tmp_path / "bucket" / folder / "sample.txt").read_bytes() == b"synthetic original"
    destination.write_bytes(b"existing local contents which must be kept")
    conflict = invoke("pull", destination)
    assert conflict.returncode != 0
    assert json_records(conflict.stdout)[-1]["status"] == "BLOCKED"
    diagnostic = json_records(conflict.stdout)[-1]["diagnostics"][0]
    assert diagnostic["code"] == "TARGET_CONFLICT"
    assert diagnostic["reason"] and diagnostic["impact"] and diagnostic["next_steps"]
    assert destination.read_bytes() == b"existing local contents which must be kept"
    (tmp_path / "bucket" / folder / "sample.txt").unlink()
    failure = invoke("pull", tmp_path / "missing.txt")
    assert failure.returncode != 0
    assert json_records(failure.stdout)[-1]["status"] == "BLOCKED"
    assert destination.read_bytes() == b"existing local contents which must be kept"


@pytest.mark.parametrize("sha256", [False, True])
def test_direct_archive_cli_without_project(tmp_path, sha256):
    source = make_tar(tmp_path)
    receipt = tmp_path / "receipt.json"
    command = [
        sys.executable, "-m", "harness.utils.transfer.archive", "extract",
        "--archive", str(source), "--destination", str(tmp_path / "restore"),
        "--include", "data/chosen/a.h5ad", "--strip-components", "2",
        "--execute", "--receipt", str(receipt), "--progress-interval", "0",
    ]
    if sha256:
        command.append("--sha256")
    result = subprocess.run(command, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "PASS"
    saved = json.loads(receipt.read_text())
    assert saved["project_id"] is None
    assert (tmp_path / "restore/a.h5ad").read_bytes() == b"gene data"
    assert ("sha256" in saved["files"][0]) == sha256


def test_partial_project_arguments_are_reported(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "harness.utils.transfer.b2", "--project", "example"],
        text=True, capture_output=True,
    )
    assert result.returncode != 0
    assert "--harness-root and --project together" in result.stderr


def test_transfer_receipt_preserves_missing_tool_explanation(tmp_path, monkeypatch, capsys):
    from harness.utils.transfer import b2

    monkeypatch.setattr(b2.shutil, "which", lambda name: None)
    receipt = tmp_path / "missing-tool.json"
    code = b2.Engine().main(argv=[
        "pull", "--file", "--local", str(tmp_path / "new.txt"),
        "--remote", "b2:bucket/new.txt", "--execute", "--receipt", str(receipt),
    ])
    saved = json.loads(receipt.read_text())
    issue = saved["diagnostics"][0]
    assert code == saved["exit_code"] != 0
    assert issue["code"] == "MISSING_TOOL"
    assert "rclone" in issue["reason"]
    assert issue["impact"] and issue["next_steps"]
    assert json_records(capsys.readouterr().out)[-1] == saved



def test_failed_archive_receipt_preserves_request_and_repair_context(tmp_path):
    from harness.utils.transfer.archive import Engine

    source = tmp_path / "missing.tar"
    destination = tmp_path / "restore"
    receipt = tmp_path / "failed.json"
    assert Engine().main(argv=[
        "extract", "--archive", str(source), "--destination", str(destination),
        "--include", "dataset", "--execute", "--receipt", str(receipt),
    ]) == 1
    saved = json.loads(receipt.read_text())
    assert saved["archive"] == str(source)
    assert saved["destination"] == str(destination)
    assert saved["include"] == ["dataset"]
    assert str(source) in saved["diagnostics"][0]["reason"]
    assert saved["diagnostics"][0]["next_steps"]
    assert not destination.exists()
