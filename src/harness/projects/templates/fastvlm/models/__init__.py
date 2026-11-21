"""Expose FastVLM checkpoint handling under its original and descriptive names."""
import sys

from . import fast_vision

fastvithd = fast_vision
sys.modules[f"{__name__}.fastvithd"] = fast_vision
