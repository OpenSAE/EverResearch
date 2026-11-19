"""目的和主要功能：采集进程亲和性、所属资源组及可见上级的共享额度和身份事实。

适用范围：Linux 本机环境采集；默认从进程归属及挂载信息定位 cgroup 第二版，
显式目录用于隔离样本。结果记录可见约束、读取状态和原因，供快照比较与展示。
"""

from __future__ import annotations

import os
from pathlib import Path
import re


def _read(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text().strip(), None
    except OSError as error:
        return None, f"{type(error).__name__}: {error.strerror or 'read failed'}"


def _limit(value: str | None) -> int | None:
    try:
        number = int(value) if value is not None else None
        return number if number is not None and number >= 0 else None
    except ValueError:
        return None


def _unescape(value: str) -> str:
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), value)


def _locate() -> tuple[Path | None, Path | None, str | None]:
    membership, error = _read(Path("/proc/self/cgroup"))
    if error:
        return None, None, f"process cgroup: {error}"
    member = next((line[3:] for line in (membership or "").splitlines()
                   if line.startswith("0::")), None)
    if member is None:
        return None, None, "cgroup v2 membership unavailable"
    member_path = Path(member)
    if not member_path.is_absolute() or ".." in member_path.parts:
        return None, None, "process cgroup path outside visible namespace"
    mounts, error = _read(Path("/proc/self/mountinfo"))
    if error:
        return None, None, f"cgroup mounts: {error}"
    candidates = []
    for line in (mounts or "").splitlines():
        left, separator, right = line.partition(" - ")
        fields = left.split()
        if not separator or not right.split() or right.split()[0] != "cgroup2":
            continue
        if len(fields) < 6:
            continue
        root, mount = (Path(_unescape(value)) for value in fields[3:5])
        if not root.is_absolute() or not mount.is_absolute() or ".." in root.parts:
            continue
        if member_path.is_relative_to(root):
            candidates.append((len(root.parts), mount, mount / member_path.relative_to(root)))
    if not candidates:
        return None, None, "matching visible cgroup v2 mount unavailable"
    # Use the widest visible mount so accessible ancestors remain observable.
    _, boundary, current = min(candidates, key=lambda candidate: candidate[0])
    return current, boundary, None


def _ceiling(raw: str | None, cpu: bool = False) -> tuple[int | float | None, str]:
    if raw is None:
        return None, "unknown"
    fields = raw.split()
    if cpu:
        if len(fields) != 2 or not _limit(fields[1]):
            return None, "unknown"
        if fields[0] == "max":
            return None, "unbounded_visible"
        quota = _limit(fields[0])
        return (quota / int(fields[1]), "observed") if quota else (None, "unknown")
    if raw == "max":
        return None, "unbounded_visible"
    number = _limit(raw)
    return number, "observed" if number is not None else "unknown"


def observe(cgroup_root: Path | None = None) -> dict:
    """Read current membership and visible ancestors; explicit directories are flat fixtures.

    Ceilings are shared by each group's subtree. Hidden ancestors and competing
    workloads can further constrain resources; values represent visible bounds.
    """
    errors = {}
    affinity_count = None
    try:
        affinity_count = len(os.sched_getaffinity(0))
    except (AttributeError, OSError) as error:
        errors["cpu_affinity"] = f"{type(error).__name__}: affinity query unavailable"
    if cgroup_root is None:
        current, boundary, location_error = _locate()
    else:
        current = boundary = Path(cgroup_root)
        location_error = None
    if location_error:
        errors["cgroup"] = location_error
    groups = []
    memory_current = None
    if current is not None:
        directory = current
        while True:
            relative = directory.relative_to(boundary)
            label = "/" if relative == Path(".") else "/" + relative.as_posix()
            item = {"path": label}
            for name, field, cpu in (("cpu.max", "cpu_quota", True),
                                     ("memory.max", "memory_limit", False)):
                raw, error = _read(directory / name)
                number, status = _ceiling(raw, cpu)
                item[field] = number
                item[field + "_status"] = status
                if error or status == "unknown":
                    errors[f"{label}:{name}"] = error or "invalid limit value"
            if directory == current:
                raw, error = _read(directory / "memory.current")
                memory_current = _limit(raw)
                if error or memory_current is None:
                    errors["memory_current"] = error or "invalid memory usage value"
            groups.append(item)
            if directory == boundary:
                break
            directory = directory.parent

    result = {
        "cpu_affinity_count": affinity_count,
        "memory_current_bytes": memory_current,
        "cgroup_path": groups[0]["path"] if groups else None,
        "cgroup_ancestors": groups,
        "errors": errors,
        "source": "sched_getaffinity, process membership and visible cgroup v2 hierarchy",
        "scope": "current cgroup usage; shared visible ancestor ceilings; hidden ancestors unknown",
    }
    for field, output, status_key in (("cpu_quota", "cpu_quota_cores", "cpu_quota_status"),
                                      ("memory_limit", "memory_limit_bytes", "memory_limit_status")):
        numbers = [item[field] for item in groups if item[field] is not None]
        complete = bool(groups) and all(item[field + "_status"] != "unknown" for item in groups)
        result[output] = min(numbers) if numbers else None
        result[status_key] = "observed" if numbers else "unbounded_visible" if complete else "unknown"
        result[field + "_complete"] = complete

    status, error = _read(Path("/proc/self/status"))
    if error:
        errors["identity_status"] = error
    fields = dict(line.split(":", 1) for line in (status or "").splitlines() if ":" in line)
    result["identity"] = {
        "uid": os.geteuid(),
        "gid": os.getegid(),
        "administrator": os.geteuid() == 0,
        "no_new_privileges": fields.get("NoNewPrivs", "").strip() == "1"
        if "NoNewPrivs" in fields
        else None,
        "seccomp_mode": _limit(fields.get("Seccomp", "").strip()),
        "container_marker_visible": Path("/.dockerenv").exists(),
        "sandbox_acceptance": "not tested",
        "source": "effective Unix identity and /proc/self/status",
    }
    return result
