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

"""Dispatch named prediction exports and load only the requested formats."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from depth_anything_3.specs import Prediction


_EXPORT_MODULES = {
    "glb": "glb",
    "mini_npz": "npz",
    "npz": "npz",
    "feat_vis": "feat_vis",
    "depth_vis": "depth_vis",
    "gs_ply": "gs",
    "gs_video": "gs",
    "colmap": "colmap",
}
SUPPORTED_EXPORT_FORMATS = frozenset(_EXPORT_MODULES)
__all__ = ["export"]


def __getattr__(name):
    """Keep individual exporters importable through the existing package."""
    if name.startswith("export_to_"):
        export_format = name[len("export_to_"):]
        if export_format in _EXPORT_MODULES:
            module = import_module(f".{_EXPORT_MODULES[export_format]}", __package__)
            return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def export(prediction: Prediction, export_format: str, export_dir: str, **kwargs):
    formats = export_format.split("-")
    for name in formats:
        if name not in SUPPORTED_EXPORT_FORMATS:
            raise ValueError(f"Unsupported export format: {name}")
    for name in formats:
        exporter = __getattr__(f"export_to_{name}")
        if name in {"mini_npz", "npz", "depth_vis"}:
            exporter(prediction, export_dir)
        else:
            exporter(prediction, export_dir, **kwargs.get(name, {}))
