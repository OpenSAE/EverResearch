"""Build the VGGT distribution from its component source directories."""

from pathlib import Path
from runpy import run_path

from setuptools import setup


packages = run_path(str(Path(__file__).parent / "base/geometry_runtime/source_layout.py"))["PACKAGES"]
setup(packages=list(packages), package_dir=packages)
