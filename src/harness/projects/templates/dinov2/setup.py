# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the Apache License, Version 2.0
# found in the LICENSE file in the root directory of this source tree.

from pathlib import Path
import re
from shutil import copy2, copytree
import runpy
from typing import List, Tuple

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist


NAME = "dinov2"
DESCRIPTION = "PyTorch code and models for the DINOv2 self-supervised learning method."

URL = "https://github.com/facebookresearch/dinov2"
AUTHOR = "FAIR"
REQUIRES_PYTHON = ">=3.9.0"
HERE = Path(__file__).resolve().parent
checkout = runpy.run_path(str(HERE / "base" / "checkout.py"))
PACKAGES = checkout["PACKAGES"]
RENAMED_MODULES = checkout["RENAMED_MODULES"]


class BuildPython(build_py):
    """Install moved source modules under their existing import names."""

    def find_package_modules(self, package, package_dir):
        public_names = {
            Path(filename).stem: fullname.rsplit(".", maxsplit=1)[1]
            for fullname, filename in RENAMED_MODULES.items()
            if fullname.rpartition(".")[0] == package
        }
        modules = super().find_package_modules(package, package_dir)
        return [
            (module_package, public_names.get(module, module), filename)
            for module_package, module, filename in modules
        ]



class SourceDistribution(sdist):
    """Include checkout launchers, installation files and accompanying documentation."""

    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        destination = Path(base_dir)
        for directory in PACKAGES.values():
            (destination / directory).mkdir(parents=True, exist_ok=True)
        for name in ("base/checkout.py", "main.py", "requirements.txt",
                     "requirements_dev.txt", "requirements_extras.txt", "CONTRIBUTING.md"):
            copy2(HERE / name, destination / name)
        for name in ("doc", "scripts", "assets", "third_party/pytorch_hub"):
            copytree(HERE / name, destination / name, dirs_exist_ok=True,
                     ignore=lambda _, names: {name for name in names if name == "__pycache__"})


try:
    with open(HERE / "README.md", encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


def get_requirements(path: str = HERE / "requirements.txt") -> Tuple[List[str], List[str]]:
    requirements = []
    extra_indices = []
    with open(path) as f:
        for line in f.readlines():
            line = line.rstrip("\r\n")
            if line.startswith("--extra-index-url "):
                extra_indices.append(line[18:])
                continue
            requirements.append(line)
    return requirements, extra_indices


def get_package_version() -> str:
    with open(HERE / PACKAGES["dinov2"] / "__init__.py") as f:
        result = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if result:
            return result.group(1)
    raise RuntimeError("Can't get package version")


requirements, extra_indices = get_requirements()
version = get_package_version()
dev_requirements, _ = get_requirements(HERE / "requirements_dev.txt")
extras_requirements, _ = get_requirements(HERE / "requirements_extras.txt")


(HERE / ".build").mkdir(exist_ok=True)

setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=list(PACKAGES),
    package_dir=PACKAGES,
    cmdclass={"build_py": BuildPython, "sdist": SourceDistribution},
    options={"build": {"build_base": ".build/objects"}, "egg_info": {"egg_base": ".build"}},
    package_data={
        "dinov2.configs.bundled": ["config.yaml", "tasks/*/config.yaml"],
        "dinov2.thirdparty.CLIP": ["LICENSE"],
    },
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "extras": extras_requirements,
    },
    dependency_links=extra_indices,
    license="Apache",
    license_files=("LICENSE", "assets/licenses/upstream/files/LICENSE_*"),
    classifiers=[
        # Trove classifiers: https://github.com/pypa/trove-classifiers/blob/main/src/trove_classifiers/__init__.py
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
