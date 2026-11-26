"""Preserve TRL's source distribution contents and local build cache location.

Setuptools executes this file when building or installing the source tree.
"""

from pathlib import Path

from setuptools import setup
from setuptools.command.sdist import sdist


class SourceDistribution(sdist):
    """Include contributor guidance while leaving checkout-only tests behind."""

    def make_distribution(self):
        self.filelist.files = [path for path in self.filelist.files if Path(path).parts[0] != "tests"]
        self.filelist.append("CONTRIBUTING.md")
        super().make_distribution()


Path(".build").mkdir(exist_ok=True)
setup(
    cmdclass={"sdist": SourceDistribution},
    options={"egg_info": {"egg_base": ".build"}, "build": {"build_base": ".build"}},
)
