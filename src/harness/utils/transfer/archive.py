"""Purpose and main function: View Local tar Content, and extract normal files and directories by the selected path.

Scope of application: Direct handling of specified compression packages or call by the project running portal; support tar.zst Waiting for compression format,
File SHA256 Summary adopted as explicitly requested --sha256 Enable.
"""

from __future__ import annotations

import argparse
import bz2
from contextlib import contextmanager
import fnmatch
import gzip
import hashlib
import json
import lzma
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile
import threading
import time


def _name(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or "\0" in value:
        raise ValueError("Unsafe archive path: " + value)
    if path.parts and ":" in path.parts[0]:
        raise ValueError("Archive path contains a drive or scheme: " + value)
    return path.as_posix().removeprefix("./").rstrip("/")


def _matches(name: str, patterns: tuple[str, ...], ignore_case: bool) -> bool:
    if ignore_case:
        name = name.casefold()
        patterns = tuple(pattern.casefold() for pattern in patterns)
    return any(
        name == pattern or name.startswith(pattern + "/") or fnmatch.fnmatchcase(name, pattern)
        for pattern in patterns
    )


@contextmanager
def _stream(source: Path, progress, interval: float):
    """Drain zstd to its end so truncated streams and checksum failures are reported."""
    # zstd inherits this raw descriptor: buffered magic-byte reads would leave
    # its OS offset ahead of the Python position and make the child skip bytes.
    with source.open("rb", buffering=0) as compressed, tempfile.TemporaryFile() as errors:
        decoder = None
        magic = compressed.read(6)
        compressed.seek(0)
        if magic.startswith(b"\x28\xb5\x2f\xfd") or source.suffix.lower() in {".zst", ".zstd"}:
            if shutil.which("zstd") is None:
                raise ValueError("tar.zst needs the zstd command on PATH")
            decoder = subprocess.Popen(
                ["zstd", "-dc"], stdin=compressed, stdout=subprocess.PIPE, stderr=errors
            )
        if decoder:
            output = decoder.stdout
        elif magic.startswith(b"\x1f\x8b"):
            output = gzip.GzipFile(fileobj=compressed)
        elif magic.startswith(b"BZh"):
            output = bz2.BZ2File(compressed)
        elif magic.startswith(b"\xfd7zXZ\x00"):
            output = lzma.LZMAFile(compressed)
        else:
            output = compressed
        stop = threading.Event()

        def report():
            while not stop.wait(interval):
                progress(os.lseek(compressed.fileno(), 0, os.SEEK_CUR))

        reporter = threading.Thread(target=report, daemon=True) if interval else None
        if reporter:
            reporter.start()
        try:
            with tarfile.open(fileobj=output, mode="r|", bufsize=1024 * 1024) as archive:
                yield archive
            while output.read(1024 * 1024):
                pass
            if decoder:
                status = decoder.wait()
                if status:
                    errors.seek(0)
                    detail = errors.read()[-2000:].decode(errors="replace").strip()
                    raise ValueError("zstd decompression failed: " + detail)
        finally:
            stop.set()
            if reporter:
                reporter.join()
            if decoder:
                output.close()
                if decoder.poll() is None:
                    decoder.terminate()
                decoder.wait()
            elif output is not compressed:
                output.close()


class Engine:
    def __init__(self, project_id=None):
        self.project_id = project_id

    @staticmethod
    def _emit(event: str, **fields):
        print(json.dumps({"event": event, **fields}, ensure_ascii=False), flush=True)

    def extract(
        self,
        archive: str,
        destination: str | None,
        *,
        include: tuple[str, ...],
        exclude: tuple[str, ...] = (),
        strip_components: int = 0,
        ignore_case: bool = False,
        reserve_gib: float = 2,
        progress_interval: float = 20,
        execute: bool = False,
        list_only: bool = False,
        keep_partial: bool = False,
        sha256: bool = False,
    ) -> dict:
        """Extract selected regular files/directories into a new destination atomically."""
        if not include:
            raise ValueError("At least one --include path or pattern is required")
        include = tuple(_name(pattern) for pattern in include)
        exclude = tuple(_name(pattern) for pattern in exclude)
        if any(pattern in {"", "."} for pattern in (*include, *exclude)):
            raise ValueError("Use an explicit path or * pattern instead of an empty selection")
        if type(strip_components) is not int or strip_components < 0:
            raise ValueError("--strip-components must be a nonnegative integer")
        if not math.isfinite(reserve_gib) or reserve_gib < 0:
            raise ValueError("--reserve-gib must be finite and nonnegative")
        if not math.isfinite(progress_interval) or progress_interval < 0:
            raise ValueError("--progress-interval must be finite and nonnegative")
        source = Path(archive).expanduser().resolve(strict=True)
        if not source.is_file():
            raise ValueError("Archive is not a regular file")
        target = None
        if not list_only:
            if not destination:
                raise ValueError("Extraction requires --destination")
            supplied = Path(destination).expanduser()
            if supplied.is_symlink():
                raise ValueError("Destination must not be a symbolic link")
            target = supplied.resolve(strict=False)
            if target == Path(target.anchor) or target.exists():
                raise ValueError("Destination must be a new non-root directory")
        record = {
            "schema": "researchharness.archive_extract.v1",
            "project_id": self.project_id,
            "sha256_requested": sha256,
            "archive": str(source),
            "destination": str(target) if target else None,
            "include": list(include),
            "exclude": list(exclude),
            "strip_components": strip_components,
            "mode": "preview" if not execute else ("list" if list_only else "extract"),
            "status": "NOT_RUN",
            "members_scanned": 0,
            "selected_members": 0,
            "files": [],
            "selected_bytes": 0,
        }
        if not execute:
            return record
        start = time.monotonic()
        staging = None
        source_stat = source.stat()
        source_identity = (
            source_stat.st_dev,
            source_stat.st_ino,
            source_stat.st_size,
            source_stat.st_mtime_ns,
        )

        def progress(position):
            self._emit(
                "progress",
                compressed_bytes_read=position,
                archive_bytes=source_stat.st_size,
                selected_bytes=record["selected_bytes"],
                files=len(record["files"]),
            )

        try:
            with _stream(source, progress, progress_interval) as stream:
                for member in stream:
                    record["members_scanned"] += 1
                    name = _name(member.name)
                    if not _matches(name, include, ignore_case) or _matches(
                        name, exclude, ignore_case
                    ):
                        continue
                    if not (member.isfile() or member.isdir()):
                        raise ValueError(
                            "Selected links and special files are unsupported: " + name
                        )
                    record["selected_members"] += 1
                    parts = PurePosixPath(name).parts[strip_components:]
                    if not parts:
                        if member.isfile():
                            raise ValueError(
                                "--strip-components removes the entire filename: " + name
                            )
                        continue
                    relative = PurePosixPath(*parts).as_posix()
                    if list_only:
                        self._emit("member", path=name, size=member.size, directory=member.isdir())
                        if member.isfile():
                            record["files"].append({"path": name, "bytes": member.size})
                            record["selected_bytes"] += member.size
                        continue
                    if staging is None:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        staging = Path(
                            tempfile.mkdtemp(
                                prefix="." + target.name + ".extract-", dir=target.parent
                            )
                        )
                    path = staging.joinpath(*parts)
                    if member.isdir():
                        path.mkdir(parents=True, exist_ok=True)
                        continue
                    if member.size + int(reserve_gib * 1024**3) > shutil.disk_usage(staging).free:
                        raise ValueError("Insufficient disk space for " + name)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    digest = hashlib.sha256() if sha256 else None
                    copied = 0
                    with stream.extractfile(member) as input_file, path.open("xb") as output_file:
                        while chunk := input_file.read(1024 * 1024):
                            output_file.write(chunk)
                            if digest is not None:
                                digest.update(chunk)
                            copied += len(chunk)
                    if copied != member.size:
                        raise ValueError("Truncated archive member: " + name)
                    path.chmod((member.mode & 0o777) | 0o600)
                    os.utime(path, (member.mtime, member.mtime))
                    entry = {"path": relative, "bytes": copied}
                    if digest is not None:
                        entry["sha256"] = digest.hexdigest()
                    record["files"].append(entry)
                    record["selected_bytes"] += copied
            current = source.stat()
            if source_identity != (
                current.st_dev,
                current.st_ino,
                current.st_size,
                current.st_mtime_ns,
            ):
                raise ValueError("Archive changed while it was being read")
            if not record["selected_members"]:
                raise ValueError("No archive members matched the selection")
            if not list_only:
                if staging is None:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    staging = Path(
                        tempfile.mkdtemp(prefix="." + target.name + ".extract-", dir=target.parent)
                    )
                if target.exists() or target.is_symlink():
                    raise ValueError(
                        "Destination appeared during extraction; refusing to replace it"
                    )
                staging.rename(target)
                staging = None
            record.update(status="PASS", elapsed_seconds=time.monotonic() - start)
            return record
        except BaseException as error:
            if staging is not None:
                if keep_partial:
                    self._emit("partial_preserved", path=str(staging))
                else:
                    shutil.rmtree(staging)
            self._emit("failed", message=str(error), selected_bytes=record["selected_bytes"])
            raise

    def main(self, *, argv=None) -> int:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("action", choices=("list", "extract"))
        parser.add_argument("--archive", required=True)
        parser.add_argument("--destination")
        parser.add_argument("--include", action="append", required=True)
        parser.add_argument("--exclude", action="append", default=[])
        parser.add_argument("--strip-components", type=int, default=0)
        parser.add_argument("--ignore-case", action="store_true")
        parser.add_argument("--reserve-gib", type=float, default=2)
        parser.add_argument("--progress-interval", type=float, default=20)
        parser.add_argument("--keep-partial", action="store_true")
        parser.add_argument(
            "--sha256", action="store_true",
            help="Compute file SHA256 digests when explicitly requested",
        )
        parser.add_argument("--receipt", type=Path)
        parser.add_argument("--execute", action="store_true")
        args = parser.parse_args(argv)
        if args.receipt is not None and args.receipt.exists():
            parser.error("Receipt already exists; choose a new immutable receipt path")
        try:
            result = self.extract(
                args.archive,
                args.destination,
                include=tuple(args.include),
                exclude=tuple(args.exclude),
                strip_components=args.strip_components,
                ignore_case=args.ignore_case,
                reserve_gib=args.reserve_gib,
                progress_interval=args.progress_interval,
                execute=args.execute,
                list_only=args.action == "list",
                keep_partial=args.keep_partial,
                sha256=args.sha256,
            )
        except (OSError, EOFError, ValueError, tarfile.TarError) as error:
            result = {
                "schema": "researchharness.archive_extract.v1",
                "status": "FAILED",
                "project_id": self.project_id,
                "archive": str(Path(args.archive).expanduser().absolute()),
                "destination": str(Path(args.destination).expanduser().absolute()) if args.destination else None,
                "include": args.include,
                "exclude": args.exclude,
                "strip_components": args.strip_components,
                "error": str(error),
                "diagnostics": [{
                    "code": type(error).__name__,
                    "reason": str(error),
                    "impact": "This compression package is not finished and the original compression package is maintained for readback.",
                    "next_steps": ["Modify the compression package, filter parameters or target position based on specific errors, and re-execut."],
                }],
            }
        if args.receipt is not None:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            with args.receipt.open("x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            from harness.core.workspace import record_files

            record_files([args.receipt], source=__file__, summary="Write local transfer receipt")
        summary = {key: value for key, value in result.items() if key != "files"}
        summary["file_count"] = len(result.get("files", []))
        print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
        return 0 if result["status"] in {"PASS", "NOT_RUN"} else 1

if __name__ == "__main__":
    from harness.utils.transfer import module_main

    raise SystemExit(module_main(Engine))
