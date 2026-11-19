"""目的和主要功能：记录现场环境与工具的实际观察。

适用范围：本机环境资料采集与选定快照的读取和比较；结果按具体入口保存。

Extracted from OpenSAE/SAEBase; Apache-2.0.
"""

from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys

from harness.utils import limits, packages


class Engine:
    def __init__(self, root=None):
        self.root = Path(root or Path.cwd())

    def safe_call(self, args: list[str], timeout: int = 5) -> str | None:
        _rh = self
        if shutil.which(args[0]) is None:
            return None
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if p.returncode != 0:
            return None
        return p.stdout.strip()

    def cpu_info(self):
        _rh = self
        result = {
            "logical_count": os.cpu_count(),
            "physical_count": None,
            "model": None,
            "source": "python/os",
        }
        if Path("/proc/cpuinfo").exists():
            try:
                lines = Path("/proc/cpuinfo").read_text(errors="replace").splitlines()
                blocks = Path("/proc/cpuinfo").read_text(errors="replace").split("\n\n")
                pairs = set()
                for block in blocks:
                    values = {
                        key.strip(): value.strip()
                        for line in block.splitlines()
                        if ":" in line
                        for key, value in [line.split(":", 1)]
                    }
                    if "physical id" in values and "core id" in values:
                        pairs.add((values["physical id"].strip(), values["core id"].strip()))
                if pairs:
                    result["physical_count"] = len(pairs)
                models = [
                    line.split(":", 1)[1].strip() for line in lines if line.startswith("model name")
                ]
                if models:
                    result["model"] = models[0]
                    result["source"] = "/proc/cpuinfo"
            except OSError:
                pass
        return result

    def memory_info(self):
        _rh = self
        out = {"total_bytes": None, "available_bytes": None, "source": "unknown"}
        mem = Path("/proc/meminfo")
        if mem.exists():
            try:
                vals = {}
                for line in mem.read_text().splitlines():
                    if ":" in line:
                        k, rest = line.split(":", 1)
                        vals[k] = int(rest.strip().split()[0]) * 1024
                out.update(
                    {
                        "total_bytes": vals.get("MemTotal"),
                        "available_bytes": vals.get("MemAvailable"),
                        "source": "/proc/meminfo",
                    }
                )
            except (OSError, ValueError, IndexError):
                pass
        return out

    def gpu_info(self):
        _rh = self
        value = _rh.safe_call(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ]
        )
        if not value:
            return {"status": "unknown", "devices": [], "source": "nvidia-smi unavailable"}
        devices = []
        for i, line in enumerate(value.splitlines()):
            fields = [x.strip() for x in line.split(",")]
            if len(fields) < 3:
                continue
            try:
                mib = int(float(fields[1]))
            except ValueError:
                mib = None
            devices.append(
                {"index": i, "name": fields[0], "memory_mib": mib, "driver_version": fields[2]}
            )
        return {
            "status": "observed" if devices else "unknown",
            "devices": devices,
            "source": "nvidia-smi",
        }

    def storage_info(self):
        _rh = self
        usage = shutil.disk_usage(str(self.root))
        return {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "source": "shutil.disk_usage",
            "path_label": "project filesystem (absolute path intentionally omitted)",
        }

    def run_capabilities(self):
        _rh = self
        tools = ["tmux", "sbatch", "docker", "podman", "python", "nvidia-smi", "rclone"]
        return {
            "commands": {c: bool(shutil.which(c)) for c in tools},
            "virtual_environment": sys.prefix != sys.base_prefix,
            "python_version": platform.python_version(),
            "python_executable": Path(sys.executable).name,
            "cuda_visible_devices_set": "CUDA_VISIBLE_DEVICES" in os.environ,
            "sandbox": "unknown",
            "network": "not probed",
            "source": "PATH, sys and environment presence flags",
        }

    def profile(self):
        _rh = self
        node = platform.node()
        return {
            "schema_version": 1,
            "kind": "environment_profile",
            "synthetic": False,
            "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "hostname_hash": hashlib.sha256(node.encode("utf-8")).hexdigest()[:12]
            if node
            else None,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "source": "platform",
            },
            "cpu": _rh.cpu_info(),
            "memory": _rh.memory_info(),
            "gpu": _rh.gpu_info(),
            "storage": _rh.storage_info(),
            "execution": _rh.run_capabilities(),
            "limits": limits.observe(),
            "packages": packages.observe(),
            "notes": [
                "Unknown fields are intentionally not guessed",
                "No cloud credentials, env values, or absolute user paths are collected",
                "Host resources, visible process ceilings and package metadata have separate scopes",
                "PATH presence is not an execution check; GPU diagnostics are not compute acceptance",
            ],
        }

    def main(self, *, argv=None):
        _rh = self
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument(
            "--output",
            help="Optional destination JSON. Defaults to stdout; snapshots belong in the local workspace.",
        )
        parser.add_argument("--path", type=Path, default=self.root, help="Filesystem to observe")
        args = parser.parse_args(argv)
        self.root = args.path
        data = _rh.profile()
        serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            dest = Path(args.output)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(serialized, encoding="utf-8")
            from harness.core.workspace import record_files

            record_files(
                [dest],
                source=__file__,
                summary="Write environment snapshot",
            )
            print(f"WROTE {dest} (local runtime facts)")
        else:
            print(serialized, end="")
        return 0

if __name__ == "__main__":
    raise SystemExit(Engine().main())
