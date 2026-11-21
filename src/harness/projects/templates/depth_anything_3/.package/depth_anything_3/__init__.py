"""Expose the checkout's component sources under their public Python package."""

from pathlib import Path

__path__.append(str(Path(__file__).resolve().parents[2] / "base" / "depth_anything"))

from ._checkout import install

install()
