"""Purpose and main function: Comparison of resources, dependency, identity and limited observation status for selected environmental snapshots.

Scope of application: reading and comparison of in-house environmental information collection with selected snapshots; results stored by specific entry.

Extracted from OpenSAE/SAEBase; Apache-2.0.
"""

import argparse
import json
from pathlib import Path


class Engine:
    FIELDS = (
        "platform.system",
        "platform.machine",
        "cpu.logical_count",
        "cpu.model",
        "memory.total_bytes",
        "gpu.status",
        "gpu.devices",
        "storage.total_bytes",
        "execution.python_version",
        "execution.commands",
        "limits.cpu_affinity_count",
        "limits.cpu_quota_cores",
        "limits.cpu_quota_status",
        "limits.cpu_quota_complete",
        "limits.memory_limit_bytes",
        "limits.memory_limit_status",
        "limits.memory_limit_complete",
        "limits.identity",
        "packages.versions",
    )

    def at(self, obj, path):
        _rh = self
        for key in path.split("."):
            if not isinstance(obj, dict) or key not in obj:
                return None
            obj = obj[key]
        return obj

    def main(self, *, argv=None):
        _rh = self
        p = argparse.ArgumentParser(description=__doc__)
        p.add_argument("before")
        p.add_argument("after")
        args = p.parse_args(argv)
        a = json.loads(Path(args.before).read_text())
        b = json.loads(Path(args.after).read_text())
        if a.get("synthetic") or b.get("synthetic"):
            print(
                "WARNING: synthetic profile present; the comparison includes example data"
            )
        diff = [
            {"field": f, "before": _rh.at(a, f), "after": _rh.at(b, f)}
            for f in _rh.FIELDS
            if _rh.at(a, f) != _rh.at(b, f)
        ]
        print(json.dumps({"changes": diff, "count": len(diff)}, ensure_ascii=False, indent=2))
        return 0

if __name__ == "__main__":
    raise SystemExit(Engine().main())
