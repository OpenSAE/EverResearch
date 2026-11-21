"""Expose legacy module names for the Mosaic and Qwen model classes."""
import sys

from . import mosaic_language, qwen_language

llava_mpt = mosaic_language
llava_qwen = qwen_language
sys.modules[f"{__name__}.llava_mpt"] = mosaic_language
sys.modules[f"{__name__}.llava_qwen"] = qwen_language
