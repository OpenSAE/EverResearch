"""Keep build and metadata products under the local maintenance directory."""

from pathlib import Path

from setuptools import setup


maintenance = Path(".everresearch")
options = {}
if maintenance.is_dir():
    options = {
        "build": {"build_base": str(maintenance / "build")},
        "egg_info": {"egg_base": str(maintenance)},
    }
setup(options=options)
