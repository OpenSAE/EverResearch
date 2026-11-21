"""Expose the FastVLM runtime and components from a checkout or an installed package."""
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location
from pathlib import Path
import sys

_checkout = Path(__file__).resolve().parents[2]
SOURCE_ROOT = _checkout if (_checkout / "conf/config.json").is_file() else None


class CheckoutLlava(MetaPathFinder):
    """Resolve the LLaVA package from its source location without an installation."""

    def find_spec(self, fullname, path=None, target=None):
        locations = {
            "llava": "base/language_vision",
            "llava.serve.cli": "tasks/serve/interactive",
            "llava.train.train_qwen": "tasks/train/qwen_model",
        }
        location = locations.get(fullname)
        if location is not None:
            return spec_from_file_location(fullname, SOURCE_ROOT / location / "__init__.py")
        return None


if SOURCE_ROOT is not None:
    __path__.append(str(SOURCE_ROOT))
    sys.meta_path.insert(0, CheckoutLlava())

from . import commands

cli = commands
sys.modules[f"{__name__}.cli"] = commands
