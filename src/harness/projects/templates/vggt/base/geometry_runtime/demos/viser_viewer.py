"""Forward the existing import to vggt.viewer.viser_app."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("vggt.viewer.viser_viewer")
