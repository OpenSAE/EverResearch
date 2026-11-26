"""Keep Python import names stable when a checkout source file has moved.

Setuptools uses this mapping for the wheel and source distribution. Editable
installs use the same table in the package's checkout module finder.
"""

from pathlib import Path
from runpy import run_path

from setuptools import setup
from setuptools.command.build_py import build_py

MODULE_FILENAMES = run_path(str(Path(__file__).resolve().parent / "base/detector/runtime/module_paths.py"))[
    "MODULE_FILENAMES"
]
PUBLIC_MODULE_NAMES = {
    (name.rpartition(".")[0], filename): name.rpartition(".")[2] for name, filename in MODULE_FILENAMES.items()
}


class BuildPublicModules(build_py):
    """Store each module in the wheel under its established Python name."""

    def find_package_modules(self, package: str, package_dir: str) -> list[tuple[str, str, str]]:
        """Return the publishable module name alongside its physical source path."""
        return [
            (owner, PUBLIC_MODULE_NAMES.get((owner, module), module), path)
            for owner, module, path in super().find_package_modules(package, package_dir)
        ]


if __name__ == "__main__":
    (Path(__file__).resolve().parent / ".build_metadata").mkdir(exist_ok=True)
    setup(cmdclass={"build_py": BuildPublicModules})
