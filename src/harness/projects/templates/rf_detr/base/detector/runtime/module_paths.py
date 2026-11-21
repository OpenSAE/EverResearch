"""Locate relocated implementations under their published Python module names.

Editable installations use the source filenames. Wheel builds consume the same
table to preserve standard downstream imports, type checking and serialization.
"""

import importlib.abc
import importlib.machinery
import importlib.util
import sys
from collections.abc import Sequence
from types import ModuleType

# Each implementation lives beside the original package's other modules.
MODULE_FILENAMES = {
    "rfdetr.cli.webdataset": "pack_dataset",
    "rfdetr.datasets.io_utils": "image_loading",
    "rfdetr.datasets.o365": "objects_dataset",
    "rfdetr.datasets.yolo": "yolo_dataset",
    "rfdetr.datasets.yolo_yaml": "yolo_configuration",
    "rfdetr.detr": "detector",
    "rfdetr.evaluation.f1_sweep": "threshold_sweep",
    "rfdetr.export.backend": "export_backend",
    "rfdetr.export.executorch.xnnpack": "delegate_partition",
    "rfdetr.export.resize": "image_resize",
    "rfdetr.export.runtime.preprocess": "preprocessing",
    "rfdetr.export.topk": "score_selection",
    "rfdetr.models.backbone.dinov2": "dino_backbone",
    "rfdetr.models.backbone.dinov2_specs": "dino_architectures",
    "rfdetr.models.backbone.dinov2_with_windowed_attn": "dino_windowed_attention",
    "rfdetr.models.heads.keypoints": "keypoint_heads",
    "rfdetr.models.lwdetr": "detection_transformer",
    "rfdetr.models.postprocess": "postprocessing",
    "rfdetr.runtime.namespace": "argument_namespace",
    "rfdetr.training.callbacks.ema": "moving_average",
    "rfdetr.training.cli": "command_line",
    "rfdetr.utilities.io": "checkpoint_loading",
    "rfdetr.utilities.keypoints": "keypoint_geometry",
    "rfdetr.visualize.keypoints": "keypoint_drawing",
}


class CheckoutModuleFinder(importlib.abc.MetaPathFinder):
    """Resolve the installed package's module names against the editable checkout."""

    def find_spec(
        self, fullname: str, path: Sequence[str] | None = None, target: ModuleType | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        """Use Python's normal source loader and preserve the requested module name."""
        filename = MODULE_FILENAMES.get(fullname)
        if filename is None or path is None:
            return None
        parent, _, _ = fullname.rpartition(".")
        source = importlib.machinery.PathFinder.find_spec(f"{parent}.{filename}", path)
        if source is None or source.origin is None:
            return None
        return importlib.util.spec_from_file_location(fullname, source.origin)


def install_checkout_module_finder() -> None:
    """Register the checkout fallback after the standard finders."""
    if not any(isinstance(finder, CheckoutModuleFinder) for finder in sys.meta_path):
        sys.meta_path.append(CheckoutModuleFinder())
