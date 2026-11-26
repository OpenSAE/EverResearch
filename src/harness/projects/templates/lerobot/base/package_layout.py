"""Build LeRobot's public Python packages from their project-owned source directories.

Both regular and editable installations use the same module and resource mapping.
"""

from collections import defaultdict
import json
from pathlib import Path

from setuptools.command.build_py import build_py
from setuptools.command.editable_wheel import _LinkTree, _empty_dir, editable_wheel


LAYOUT_FILE = Path("conf/base/config.json")
LAYOUT = json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
PACKAGE_DIRECTORIES = LAYOUT["package_directories"]
MODULE_DIRECTORIES = defaultdict(list)
RELOCATED_FILES = set()
for qualified_name, source in LAYOUT["relocated_modules"].items():
    package, name = qualified_name.rsplit(".", 1)
    MODULE_DIRECTORIES[package].append((package, name, source))
    RELOCATED_FILES.add(Path(source))
RESOURCES = LAYOUT["package_resources"]


class BuildProjectPackages(build_py):
    """Find modules and include resources at the established installed paths."""

    def find_package_modules(self, package, package_dir):
        discovered = super().find_package_modules(package, package_dir)
        return [
            module for module in discovered if Path(module[-1]) not in RELOCATED_FILES
        ] + MODULE_DIRECTORIES.get(package, [])

    def _get_package_data_output_mapping(self):
        yield from super()._get_package_data_output_mapping()
        for target, source in RESOURCES.items():
            yield str(Path(self.build_lib, target)), source

    def get_source_files(self):
        return [
            *super().get_source_files(),
            *RESOURCES.values(),
            str(LAYOUT_FILE),
            __file__,
        ]


class EditableProjectPackages(editable_wheel):
    """Use a linked install so moved source files keep their public module names."""

    def _select_strategy(self, name, tag, build_lib):
        linked_sources = Path(self.project_dir, ".build", f"__editable__.{name}-{tag}")
        return _LinkTree(self.distribution, name, _empty_dir(linked_sources), build_lib)
