"""Forward the existing import to vggt.models.demo_inference."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("vggt.models.demo_inference")
