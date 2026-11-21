"""Purpose and main function: Read the installation version through package metadata.

Scope of application: reading and comparison of in-house environmental information collection with selected snapshots; results stored by specific entry.
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
