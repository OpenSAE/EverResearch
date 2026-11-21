"""Forward the existing import to vggt.scene_data.images."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("vggt.scene_data.images")
