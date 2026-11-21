"""Expose the model and legacy LLaVA command packages from a checkout or wheel."""
from pathlib import Path
import sys

_checkout = Path(__file__).resolve().parents[2]
SOURCE_ROOT = _checkout if (_checkout / "conf/config.json").is_file() else None
if SOURCE_ROOT is not None:
    __path__.extend([str(SOURCE_ROOT / "models"), str(SOURCE_ROOT / "tasks")])

from . import image_processing, service_logging

mm_utils = image_processing
utils = service_logging
sys.modules[f"{__name__}.mm_utils"] = image_processing
sys.modules[f"{__name__}.utils"] = service_logging

from .model import LlavaLlamaForCausalLM, LlavaQwen2ForCausalLM
