"""Forward the existing import to vggt.viewer.gradio_app."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("vggt.viewer.gradio_viewer")
