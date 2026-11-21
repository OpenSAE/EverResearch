"""Purpose and main function: Preview or execution of documents B2 Upload, download and on-demand verification.

Scope of application: Transmission of documents by clear source, target and range; verify and independence SHA256 Verify
Only after a specific human request or approval has been made, general upload download to record the completion of the transmission results.
Extracted from OpenSAE/SAEBase; Apache-2.0.
"""

from __future__ import annotations
import argparse
from collections import deque
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


class Engine:
    def __init__(self, project_id=None):
        self.project_id = project_id

    def remote_path(self, text: str) -> str:
        """Parse a configured remote, bucket and explicit object path."""
        match = re.fullmatch(r"[A-Za-z0-9_-]+:[A-Za-z0-9._-]+/(.+)", text or "")
        if match is None or any(ord(c) < 32 or ord(c) == 127 for c in text):
            raise ValueError("Remote must be configured-remote:bucket/path")
        path = match.group(1)
        if not path.strip("/"):
            raise ValueError("Remote must select a path inside the bucket")
        if ".." in path.split("/"):
            raise ValueError("Parent directory segment is not allowed")
        return text

    def local_path(self, text: str, needs_exist: bool, *, single_file: bool = False) -> str:
        path = Path(text).expanduser().resolve(strict=False)
        if needs_exist and not (path.is_file() if single_file else path.is_dir()):
            kind = "file" if single_file else "directory"
            raise ValueError(f"Local source {kind} not found: {path}")
        if path.exists() and (path.is_dir() if single_file else path.is_file()):
            raise ValueError("Local path type disagrees with --file")
        if path == Path(path.anchor):
            raise ValueError("Refusing a filesystem root as transfer scope")
        return str(path)

    def command(
        self,
        action: str,
        local: str,
        remote: str,
        transfers: int = 16,
        checkers: int = 16,
        *,
        execute: bool = False,
        streams: int = 4,
        fast_list: bool = True,
        chunk_size: str = "64M",
        cutoff: str = "256M",
        retries: int = 10,
        low_level_retries: int = 20,
        upload_concurrency: int = 4,
        single_file: bool = False,
        include: tuple[str, ...] = (),
        exclude: tuple[str, ...] = (),
        connect_timeout: str = "15s",
        timeout: str = "5m",
        retries_sleep: str = "10s",
    ) -> list[str]:
        """Construct safe, explicit rclone argv without reading credentials."""
        if action not in ("push", "pull", "verify"):
            raise ValueError("Unsupported transfer action")
        if (
            not 1 <= transfers <= 64
            or not 1 <= checkers <= 64
            or (not 1 <= streams <= 16)
            or (not 1 <= upload_concurrency <= 16)
            or (not 1 <= retries <= 20)
            or (not 1 <= low_level_retries <= 40)
        ):
            raise ValueError("Transfer performance settings out of bounds")
        if not re.fullmatch("[1-9][0-9]*[KMG]", chunk_size):
            raise ValueError("Invalid transfer chunk size")
        if not re.fullmatch("[1-9][0-9]*[KMG]", cutoff):
            raise ValueError("Invalid multithread cutoff")
        for duration in (connect_timeout, timeout, retries_sleep):
            if not re.fullmatch(r"[1-9][0-9]*(?:ms|s|m|h)", duration):
                raise ValueError("Timeouts and retry delay need a positive duration, e.g. 15s")
        for pattern in (*include, *exclude):
            if not pattern or any(character in pattern for character in "\0\r\n"):
                raise ValueError("Filters must be nonempty single-line patterns")
        r = self.remote_path(remote)
        local_ref = self.local_path(local, action in ("push", "verify"), single_file=single_file)
        source, dest = (local_ref, r) if action in ("push", "verify") else (r, local_ref)
        op = "check" if action == "verify" else ("copyto" if single_file else "copy")
        if action == "verify" and single_file:
            if Path(local_ref).name != r.rsplit("/", 1)[1]:
                raise ValueError(
                    "Single-file verification requires matching local and remote names"
                )
            # rclone check accepts a source file but requires a destination directory.
            dest = r.rsplit("/", 1)[0]
        args = [
            "rclone",
            op,
            source,
            dest,
            "--transfers",
            str(transfers),
            "--checkers",
            str(checkers),
            "--retries",
            str(retries),
            "--low-level-retries",
            str(low_level_retries),
            "--stats",
            "10s",
            "--stats-one-line",
            "--contimeout",
            connect_timeout,
            "--timeout",
            timeout,
            "--retries-sleep",
            retries_sleep,
        ]
        for option, patterns in (("--include", include), ("--exclude", exclude)):
            for pattern in patterns:
                args.extend((option, pattern))
        if fast_list:
            args.append("--fast-list")
        if action == "verify":
            args += ["--one-way"]
        else:
            args += [
                "--immutable",
                "--multi-thread-streams",
                str(streams),
                "--multi-thread-cutoff",
                cutoff,
                "--multi-thread-chunk-size",
                chunk_size,
            ]
            if action == "push":
                args += [
                    "--b2-chunk-size",
                    chunk_size,
                    "--b2-upload-concurrency",
                    str(upload_concurrency),
                ]
        if single_file and action != "verify":
            args.append("--ignore-existing")
        if not execute and action != "verify":
            args += ["--dry-run"]
        return args

    def _run_command(self, cmd: list[str]) -> tuple[int, str]:
        """Stream progress and retain a bounded tail explaining an unsuccessful transfer."""
        lines = deque(maxlen=40)
        with subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True) as process:
            for line in process.stderr:
                print(line, end="", file=sys.stderr, flush=True)
                lines.append(line)
            code = process.wait()
        return code, "".join(lines)[-8000:]

    def _transfer_file(self, cmd: list[str]) -> tuple[int, str]:
        """Reject an observed target conflict, then preserve existing destinations."""
        preview = cmd.copy()
        preview.remove("--ignore-existing")
        preview.extend(("--dry-run", "--differ", "-"))
        result = subprocess.run(preview, capture_output=True, text=True, check=False)
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode:
            return result.returncode, result.stderr[-8000:]
        if result.stdout.strip():
            print("Source and destination differ; existing target preserved", file=sys.stderr)
            return 6, "Source and destination differ; existing target preserved"
        return self._run_command(cmd)

    def _utc(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def main(self, *, argv=None) -> int:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument(
            "action", choices=("push", "pull", "verify"),
            help="push/pull Transfer File; verify Only after a specific human request or approval has been made",
        )
        parser.add_argument("--local", required=True)
        parser.add_argument("--remote", required=True)
        parser.add_argument("--transfers", type=int, default=16)
        parser.add_argument("--checkers", type=int, default=16)
        parser.add_argument("--streams", type=int, default=4)
        parser.add_argument("--cutoff", default="256M")
        parser.add_argument("--chunk-size", default="64M")
        parser.add_argument("--upload-concurrency", type=int, default=4)
        parser.add_argument("--retries", type=int, default=10)
        parser.add_argument("--low-level-retries", type=int, default=20)
        parser.add_argument("--no-fast-list", action="store_true")
        parser.add_argument(
            "--file", action="store_true", help="Transfer one explicitly named file"
        )
        parser.add_argument(
            "--include", action="append", default=[], help="Repeatable rclone filter"
        )
        parser.add_argument(
            "--exclude", action="append", default=[], help="Repeatable rclone filter"
        )
        parser.add_argument("--connect-timeout", default="15s")
        parser.add_argument("--timeout", default="5m")
        parser.add_argument("--retries-sleep", default="10s")
        parser.add_argument("--receipt", type=Path, help="Unique immutable local result receipt")
        parser.add_argument("--execute", action="store_true", help="Explicitly access B2")
        args = parser.parse_args(argv)
        try:
            cmd = self.command(
                args.action,
                args.local,
                args.remote,
                args.transfers,
                args.checkers,
                execute=args.execute,
                streams=args.streams,
                fast_list=not args.no_fast_list,
                chunk_size=args.chunk_size,
                cutoff=args.cutoff,
                retries=args.retries,
                low_level_retries=args.low_level_retries,
                upload_concurrency=args.upload_concurrency,
                single_file=args.file,
                include=tuple(args.include),
                exclude=tuple(args.exclude),
                connect_timeout=args.connect_timeout,
                timeout=args.timeout,
                retries_sleep=args.retries_sleep,
            )
            if args.receipt is not None and args.receipt.exists():
                raise ValueError("Receipt already exists; choose a new immutable receipt path")
        except ValueError as exc:
            parser.error(str(exc))
        record = {
            "schema": "saebase.b2_transfer.v1",
            "action": args.action,
            "mode": "execute" if args.execute else "preview",
            "rclone_args": cmd,
            "project_id": self.project_id,
            "status": "RUNNING" if args.execute else "NOT_RUN",
            "started_utc": self._utc(),
        }
        print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
        if not args.execute:
            return 0
        start = time.monotonic()
        if shutil.which("rclone") is None:
            code = 2
            detail = "rclone is not installed"
            print(detail, file=sys.stderr)
        else:
            try:
                code, detail = (
                    self._transfer_file(cmd)
                    if args.file and args.action != "verify"
                    else self._run_command(cmd)
                )
            except OSError as exc:
                code = 2
                detail = f"{type(exc).__name__}: {exc}"
                print(f"rclone execution error: {exc}", file=sys.stderr)
        record.update(
            {
                "exit_code": code,
                "status": "PASS" if code == 0 else "BLOCKED",
                "elapsed_seconds": time.monotonic() - start,
                "finished_utc": self._utc(),
                "remote_integrity": "CHECKED"
                if args.action == "verify" and code == 0
                else "NOT_RUN",

            }
        )
        if code:
            if detail == "rclone is not installed":
                category = "MISSING_TOOL"
                analysis = "The transfer program has not been started and this file transfer cannot be executed."
                next_steps = ["Install rclone or amendment PATH,Enables the current environment to find the command and retry using original parameters."]
            elif "Source and destination differ; existing target preserved" in detail:
                category = "TARGET_CONFLICT"
                analysis = "The source is different from the existing target content, this copy has been stopped and the target document remains as it is."
                next_steps = ["Confirm what should be retained and try again after selecting a new target filename or directory for this transfer."]
            else:
                category = "TRANSFER_ERROR"
                analysis = "The transmission process was not successfully completed and this request is not yet complete."
                next_steps = ["Check for source, target, connection configuration or access conditions based on error output, and try again with original parameters."]
            record["diagnostics"] = [{
                "code": category,
                "reason": detail.strip() or f"rclone exited with code {code}",
                "impact": analysis,
                "next_steps": next_steps,
            }]
        if args.receipt is not None:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            with args.receipt.open("x", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
                f.write("\n")
            from harness.core.workspace import record_files

            record_files([args.receipt], source=__file__, summary="Write local transfer receipt")
        print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
        return code

if __name__ == "__main__":
    from harness.utils.transfer import module_main

    raise SystemExit(module_main(Engine))
