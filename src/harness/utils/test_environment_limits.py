"""Purpose and main function: Replicating resource limitation collection and its snapshot and comparative behaviour.

Scope of application: Environmental retrievation tests performed by users on a needs basis; screening snapshots and comparisons using quarantined input.
"""
import copy
import json
from pathlib import Path

import pytest

from harness.utils import compare, limits, probe


def save(directory, name, value):
    (directory / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def group(path, cpu="200000 100000", memory="1073741824", current="536870912"):
    path.mkdir(parents=True, exist_ok=True)
    for name, value in {"cpu.max": cpu, "memory.max": memory, "memory.current": current}.items():
        (path / name).write_text(value)


def redirect(monkeypatch, root, membership="/job"):
    original = Path.read_text
    def read(path, *args, **kwargs):
        if path == Path("/proc/self/cgroup"):
            return "0::" + membership + "\n"
        if path == Path("/proc/self/mountinfo"):
            return "31 20 0:30 / /sys/fs/cgroup ro - cgroup2 cgroup rw\n"
        if path.is_relative_to("/sys/fs/cgroup"):
            path = root / path.relative_to("/sys/fs/cgroup")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", read)


def test_live_identity_and_affinity():
    result = limits.observe()
    if hasattr(limits.os, "sched_getaffinity"):
        assert result["cpu_affinity_count"] == len(limits.os.sched_getaffinity(0))
    assert result["identity"]["uid"] == getattr(limits.os, "geteuid", lambda: None)()
    assert result["identity"]["gid"] == getattr(limits.os, "getegid", lambda: None)()
    assert result["identity"]["sandbox_acceptance"] == "not tested"


def test_live_cgroup_v2_observation(tmp_path):
    current, boundary, error = limits._locate()
    if error:
        pytest.skip(error)

    def available(directory, name):
        try:
            return (directory / name).read_text().strip()
        except OSError:
            return None

    visible_groups = (current, *(p for p in current.parents if p.is_relative_to(boundary)))
    cpu = [value.split() for group in visible_groups if (value := available(group, "cpu.max"))]
    memory = [value for group in visible_groups if (value := available(group, "memory.max"))]
    if not cpu and not memory:
        pytest.skip("No visible cgroup v2 CPU or memory limits")

    result = limits.observe()
    quotas = [int(quota) / int(period) for quota, period in cpu if quota != "max"]
    memory_limits = [int(value) for value in memory if value != "max"]
    if cpu:
        assert result["cpu_quota_cores"] == min(quotas, default=None)
    if memory:
        assert result["memory_limit_bytes"] == min(memory_limits, default=None)
    save(tmp_path, "live_observation.json", {
        "membership": Path("/proc/self/cgroup").read_text(),
        "cpu_limits": cpu, "memory_limits": memory, "observed": result,
    })


def test_cgroup_v1_keeps_identity_and_reports_unknown_limits(monkeypatch):
    def read(path):
        if path == Path("/proc/self/cgroup"):
            return "2:cpu,cpuacct:/job\n3:memory:/job", None
        if path == Path("/proc/self/status"):
            return "NoNewPrivs: 0", None
        raise AssertionError(f"Unexpected cgroup read: {path}")

    monkeypatch.setattr(limits, "_read", read)
    monkeypatch.setattr(limits.sys, "platform", "linux")
    result = limits.observe()
    assert result["errors"]["cgroup"] == "cgroup v2 membership unavailable"
    assert result["cpu_quota_status"] == result["memory_limit_status"] == "unknown"
    assert result["cpu_quota_cores"] is result["memory_limit_bytes"] is None
    assert result["identity"]["uid"] == getattr(limits.os, "geteuid", lambda: None)()


@pytest.mark.parametrize("cpu,memory,expected_cpu,expected_memory,status", [
    ("768000 100000", "1024", 7.68, 1024, "observed"),
    ("max 100000", "max", None, None, "unbounded_visible"),
    ("bad input", "bad input", None, None, "unknown"),
    ("100000 0", "0", None, 0, "observed"),
])
def test_flat_group(tmp_path, cpu, memory, expected_cpu, expected_memory, status):
    group(tmp_path, cpu=cpu, memory=memory, current="512")
    result = limits.observe(tmp_path)
    assert result["cpu_quota_cores"] == expected_cpu
    assert result["memory_limit_bytes"] == expected_memory
    assert result["memory_limit_status"] == status
    assert result["memory_current_bytes"] == 512


def test_missing_group_keeps_partial_observation(tmp_path):
    result = limits.observe(tmp_path)
    assert result["memory_limit_status"] == "unknown"
    assert result["memory_limit_bytes"] is None
    assert result["cpu_affinity_count"] > 0
    assert result["identity"]["uid"] == limits.os.geteuid()


def test_probe_uses_process_group(tmp_path, monkeypatch, capsys):
    root = tmp_path / "cgroup"
    group(root, "max 100000", "max", "8589934592")
    group(root / "job", "200000 100000", "1073741824", "536870912")
    redirect(monkeypatch, root)
    assert probe.Engine(tmp_path).main(argv=[]) == 0
    profile = json.loads(capsys.readouterr().out)
    save(tmp_path, "subgroup_observation.json", {"synthetic_input": True, "membership": "/job",
         "expected": {"cpu_quota_cores": 2.0, "memory_limit_bytes": 1073741824,
                      "memory_current_bytes": 536870912},
         "snapshot_limits": profile["limits"]})
    assert profile["limits"]["cpu_quota_cores"] == 2.0
    assert profile["limits"]["memory_limit_bytes"] == 1073741824
    assert profile["limits"]["memory_current_bytes"] == 536870912


def test_visible_ancestor_limit(tmp_path, monkeypatch):
    group(tmp_path, "max 100000", "max")
    group(tmp_path / "tenant", "100000 100000", "1073741824")
    leaf = tmp_path / "tenant/job"
    group(leaf, "max 100000", "max", "268435456")
    redirect(monkeypatch, tmp_path, "/tenant/job")
    result = limits.observe()
    save(tmp_path, "ancestor_observation.json", {"synthetic_input": True,
         "membership": "/tenant/job", "visible_parent": "/tenant",
         "visible_parent_cpu_cores": 1.0, "visible_parent_memory_bytes": 1073741824,
         "observed_default": result, "observed_explicit_leaf": limits.observe(leaf),
         "leaf_file_values": {"cpu.max": "max 100000", "memory.max": "max"}})
    assert result["memory_limit_status"] != "unbounded_visible"
    assert result["cpu_quota_cores"] == 1.0
    assert result["memory_limit_bytes"] == 1073741824


def test_affinity_failure_keeps_other_profile_fields(tmp_path, monkeypatch, capsys):
    def denied(pid):
        raise PermissionError(1, "synthetic sched_getaffinity denial")
    monkeypatch.setattr(limits.os, "sched_getaffinity", denied)
    try:
        probe.Engine(tmp_path).main(argv=[])
    except OSError as error:
        save(tmp_path, "affinity_failure.json", {"synthetic_input": True,
             "exception": type(error).__name__, "message": str(error),
             "stdout": capsys.readouterr().out})
        raise
    profile = json.loads(capsys.readouterr().out)
    assert profile["limits"]["cpu_affinity_count"] is None
    assert "cpu" in profile and "packages" in profile


def test_probe_json_comparison(tmp_path, capsys):
    assert probe.Engine(tmp_path).main(argv=[]) == 0
    profile = json.loads(capsys.readouterr().out)
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(json.dumps(profile))
    restored = json.loads(before.read_text())
    changed = copy.deepcopy(restored)
    changed["limits"]["cpu_quota_cores"] = 0.5
    changed["limits"]["memory_limit_bytes"] = 123456
    after.write_text(json.dumps(changed))
    assert compare.Engine().main(argv=[str(before), str(after)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert {c["field"] for c in result["changes"]} == {"limits.cpu_quota_cores", "limits.memory_limit_bytes"}
    save(tmp_path, "normal_consumer_observation.json", {"limits": restored["limits"],
         "comparison_with_synthetic_changes": result})


def test_consumers_distinguish_unknown_from_unbounded(tmp_path, capsys):
    empty = tmp_path / "missing"
    empty.mkdir()
    unbounded = tmp_path / "unbounded"
    group(unbounded, "max 100000", "max", "512")
    a = {"synthetic": False, "limits": limits.observe(empty)}
    b = {"synthetic": False, "limits": limits.observe(unbounded)}
    paths = [tmp_path / "before.json", tmp_path / "after.json"]
    for path, value in zip(paths, (a, b)):
        path.write_text(json.dumps(value))
    compare.Engine().main(argv=[str(p) for p in paths])
    comparison = json.loads(capsys.readouterr().out)
    assert any(
        change["field"] == "limits.memory_limit_status"
        for change in comparison["changes"]
    )


def mount_layout(monkeypatch, membership, mounts):
    original = Path.read_text

    def read(path, *args, **kwargs):
        if path == Path('/proc/self/cgroup'):
            return '0::' + membership + '\n'
        if path == Path('/proc/self/mountinfo'):
            return mounts
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', read)


def mount_line(root, directory):
    # mountinfo escapes whitespace in both filesystem root and mount point.
    def escape(value):
        return str(value).replace(' ', r'\040')
    return f'31 20 0:30 {escape(root)} {escape(directory)} ro - cgroup2 cgroup rw\n'


def test_mount_subtree_and_escaped_paths(tmp_path, monkeypatch):
    mount = tmp_path / 'mounted cgroup'
    group(mount, '100000 100000', '1073741824', '999')
    group(mount / 'job', '200000 100000', 'max', '512')
    mount_layout(monkeypatch, '/tenant group/job', mount_line('/tenant group', mount))
    result = limits.observe()
    assert result['cpu_quota_cores'] == 1.0
    assert result['memory_limit_bytes'] == 1073741824
    assert result['memory_current_bytes'] == 512
    assert result['cgroup_path'] == '/job'
    assert [item['path'] for item in result['cgroup_ancestors']] == ['/job', '/']
    assert result['cpu_quota_complete'] is True
    assert not result['errors']


def test_wider_mount_preserves_visible_ancestors(tmp_path, monkeypatch):
    group(tmp_path, '50000 100000', '1024')
    group(tmp_path / 'tenant', 'max 100000', 'max')
    group(tmp_path / 'tenant/job', 'max 100000', 'max')
    mounts = mount_line('/tenant', tmp_path / 'tenant') + mount_line('/', tmp_path)
    mount_layout(monkeypatch, '/tenant/job', mounts)
    result = limits.observe()
    assert result['cpu_quota_cores'] == 0.5
    assert result['memory_limit_bytes'] == 1024
    assert len(result['cgroup_ancestors']) == 3


def test_all_visible_groups_unbounded(tmp_path, monkeypatch):
    group(tmp_path, 'max 100000', 'max')
    group(tmp_path / 'job', 'max 100000', 'max', '512')
    mount_layout(monkeypatch, '/job', mount_line('/', tmp_path))
    result = limits.observe()
    assert result['memory_limit_status'] == 'unbounded_visible'
    assert result['cpu_quota_status'] == 'unbounded_visible'
    assert result['memory_limit_complete'] is True
    assert result['cpu_quota_complete'] is True
    assert result['memory_current_bytes'] == 512


def test_partial_hierarchy_preserves_known_limits_and_reason(tmp_path, monkeypatch):
    group(tmp_path, '100000 100000', '1073741824')
    group(tmp_path / 'job', 'max 100000', 'max', '512')
    mount_layout(monkeypatch, '/job', mount_line('/', tmp_path))
    original = Path.read_text

    def denied(path, *args, **kwargs):
        if path == tmp_path / 'job/memory.max' or path == tmp_path / 'cpu.max':
            raise PermissionError(13, 'synthetic permission denied')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', denied)
    result = limits.observe()
    assert result['memory_limit_bytes'] == 1073741824
    assert result['memory_limit_status'] == 'observed'
    assert result['memory_limit_complete'] is False
    assert result['cpu_quota_status'] == 'unknown'
    assert result['cpu_quota_complete'] is False
    assert 'PermissionError' in result['errors']['/job:memory.max']
    assert result['memory_current_bytes'] == 512


@pytest.mark.parametrize('membership,mounts', [
    ('/other/job', '31 20 0:30 /tenant /sys/fs/cgroup ro - cgroup2 cgroup rw\n'),
    ('/../outside', '31 20 0:30 / /sys/fs/cgroup ro - cgroup2 cgroup rw\n'),
    ('/job', ''),
])
def test_unresolved_membership_keeps_identity_and_unknowns(monkeypatch, membership, mounts):
    mount_layout(monkeypatch, membership, mounts)
    result = limits.observe()
    assert result['cpu_quota_status'] == 'unknown'
    assert result['memory_limit_status'] == 'unknown'
    assert result['memory_current_bytes'] is None
    assert result['errors']['cgroup']
    assert result['identity']['uid'] == limits.os.geteuid()


def test_old_snapshots_and_partial_limits_remain_readable(tmp_path, capsys):
    old = {"limits": {"cpu_quota_cores": 2.0, "memory_limit_bytes": 1073741824}}
    paths = [tmp_path / name for name in ("old.json", "copy.json")]
    for path in paths:
        path.write_text(json.dumps(old))
    assert compare.Engine().main(argv=[str(path) for path in paths]) == 0
    assert json.loads(capsys.readouterr().out)["count"] == 0
