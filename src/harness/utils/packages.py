"""目的和主要功能：通过包元数据读取安装版本。

适用范围：本机环境资料采集与选定快照的读取和比较；结果按具体入口保存。
"""

from __future__ import annotations

from importlib import metadata

PACKAGES = (
    "researchharness",
    "PyYAML",
    "torch",
    "transformers",
    "transformer-lens",
    "sae-lens",
    "nnsight",
    "vllm",
    "hydra-core",
    "pytest",
    "ruff",
    "playwright",
)


def observe(names=PACKAGES) -> dict:
    versions = {}
    for name in names:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return {
        "versions": versions,
        "source": "importlib.metadata",
        "scope": "distribution metadata in the current interpreter; import and execution untested",
    }
