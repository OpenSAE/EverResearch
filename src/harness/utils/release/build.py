"""Include EverResearch's public skill and project resources in Python builds.

Setuptools uses these commands for ordinary wheels and source distributions.
Editable installations load the resources directly from the checkout.
"""

from pathlib import Path

from setuptools.build_meta import build_editable as build_editable
from setuptools.build_meta import build_sdist as build_sdist
from setuptools.build_meta import build_wheel as build_wheel
from setuptools.build_meta import get_requires_for_build_editable as get_requires_for_build_editable
from setuptools.build_meta import get_requires_for_build_sdist as get_requires_for_build_sdist
from setuptools.build_meta import get_requires_for_build_wheel as get_requires_for_build_wheel
from setuptools.build_meta import prepare_metadata_for_build_editable as prepare_metadata_for_build_editable
from setuptools.build_meta import prepare_metadata_for_build_wheel as prepare_metadata_for_build_wheel
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist


def resource_manifest():
    from harness.utils.release import public_members

    return public_members(Path.cwd())[1]


class BuildResources(build_py):
    """Write the audited archive alongside the installed Python modules."""

    def run(self):
        super().run()
        if not self.editable_mode:
            from harness.utils.release import archive

            archive(Path(self.build_lib) / "harness" / "public_resources.zip", resource_manifest())


class SourceDistribution(sdist):
    """Include the original resource inputs so the sdist also builds a wheel."""

    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        for name, contents in resource_manifest().items():
            target = Path(base_dir) / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(contents)
