"""Run the FastVLM command from an uninstalled source checkout."""
import importlib.util
from pathlib import Path
import sys


def _load_checkout():
    package = Path(__file__).resolve().parent / "base/fast_vlm/__init__.py"
    spec = importlib.util.spec_from_file_location("fastvlm", package)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


if "fastvlm" not in sys.modules:
    _load_checkout()

from fastvlm.commands import main, predict

__all__ = ["predict"]

if __name__ == "__main__":
    main()
