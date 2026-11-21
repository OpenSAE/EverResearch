# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Auto-loading registry system for benchmark datasets.

This module provides registry classes that automatically discover and import
dataset implementations from the datasets subpackage on first access.
"""

import importlib
import threading

from depth_anything_3.utils.registry import Registry

__all__ = ["METRIC_REGISTRY", "MONO_REGISTRY", "MV_REGISTRY", "NVS_REGISTRY"]

# ---- Lazy import: Only scan and import all datasets submodules on first registry access ----
_loaded = False
_lock = threading.Lock()


def _import_all_datasets_once():
    """
    Scan and import all .py submodules under depth_anything_3.bench.datasets
    (skip files/packages starting with underscore), to trigger @REGISTRY.register(...) in each module.
    """
    global _loaded
    if _loaded:
        return

    with _lock:
        if _loaded:
            return

        for dataset in ("dtu", "dtu64", "eth3d", "hiroom", "scannetpp", "sevenscenes"):
            module = f"depth_anything_3.bench.datasets.{dataset}"
            try:
                importlib.import_module(module)
            except ImportError as error:
                print(f"[datasets auto-import] Failed to import {module}: {error}")

        _loaded = True


class AutoRegistry(Registry):
    """Registry that ensures all datasets are auto-discovered and imported on first use."""

    def get(self, name):
        _import_all_datasets_once()
        return super().get(name)

    def all(self):
        _import_all_datasets_once()
        return super().all()

    def has(self, name):
        _import_all_datasets_once()
        return name in self._map


# Four auto-lazy registry instances for different evaluation types
METRIC_REGISTRY = AutoRegistry()  # For metric depth evaluation
MONO_REGISTRY = AutoRegistry()  # For monocular depth evaluation
MV_REGISTRY = AutoRegistry()  # For multi-view evaluation
NVS_REGISTRY = AutoRegistry()  # For novel view synthesis evaluation

