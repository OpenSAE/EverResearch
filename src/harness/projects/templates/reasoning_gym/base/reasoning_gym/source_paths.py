"""Resolve stable Reasoning Gym import names from the maintained source layout.

The package calls this module at import time. The wheel combines the component
directories into one package. Editable installations read the same files in place.
"""

from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location
from pathlib import Path
import sys


# Existing import paths also appear in tests and serialized class references.
_PUBLIC_MODULE_PATHS = {
    "utils": "utilities",
    "algorithmic.cryptarithm": "algorithmic/letter_arithmetic",
    "arc.arc_1d": "arc/one_dimension",
    "arc.arc_1d_tasks": "arc/one_dimension_tasks",
    "arc.rearc": "arc/regeneration",
    "arc.rearc_utils": "arc/regeneration_support",
    "arithmetic.gcd": "arithmetic/greatest_common_divisor",
    "arithmetic.gsm_symbolic.generators_00_49": "arithmetic/gsm_symbolic/quantities_generators",
    "arithmetic.gsm_symbolic.generators_50_99": "arithmetic/gsm_symbolic/measurement_generators",
    "arithmetic.lcm": "arithmetic/least_common_multiple",
    "code.bf": "code/brain_language",
    "code.codeio": "code/input_output",
    "code.contrib": "code/vendor",
    "games.boxnet": "games/box_navigation",
    "games.contrib": "games/vendor",
    "games.futoshiki": "games/inequality_sudoku",
    "games.kakurasu": "games/weighted_grid",
    "games.puzzle24": "games/twenty_four",
    "games.sokoban": "games/box_pushing",
    "games.survo": "games/number_grid",
    "games.tsumego": "games/go_life_and_death",
    "induction.acre.blicket": "induction/acre/detector",
    "induction.acre.const": "induction/acre/constants",
    "logic.aiw": "logic/alice_in_wonderland",
    "logic.contrib": "logic/vendor",
}
_VENDOR_MODULES = {
    "arc.rearc_utils": ("rearc_generators", "arc/regeneration_support"),
    "code.contrib.bfit": ("bfit", "code/vendor/bfit"),
    "games.contrib.sokoban": ("sokoban", "games/vendor/sokoban"),
    "logic.contrib.logic_puzzle": ("logic_puzzle", "logic/vendor/logic_puzzle"),
}


class ReasoningGymSourceFinder(MetaPathFinder):
    """Load moved modules under the names existing consumers import."""

    def __init__(self, component_paths, project_root):
        self.component_paths = [Path(path) for path in component_paths]
        self.project_root = project_root

    def find_spec(self, fullname, path=None, target=None):
        package, _, module = fullname.partition(".")
        if package != "reasoning_gym":
            return None
        vendor = _VENDOR_MODULES.get(module)
        if vendor and self.project_root:
            upstream, _ = vendor
            source = self.project_root / "third_party" / upstream / "__init__.py"
            return spec_from_file_location(fullname, source)
        module_path = vendor[1] if vendor else _PUBLIC_MODULE_PATHS.get(module)
        if module_path is None:
            return None
        for component_path in self.component_paths:
            source = component_path / module_path
            if source.with_suffix(".py").is_file():
                return spec_from_file_location(fullname, source.with_suffix(".py"))
            if (source / "__init__.py").is_file():
                return spec_from_file_location(fullname, source / "__init__.py")
        return None


def configure_sources(package_paths):
    """Include the separately stored components when running from a checkout."""
    package_root = Path(__file__).resolve().parent
    candidate = package_root.parent.parent
    project_root = None
    if package_root.parent.name == "base" and (candidate / "pyproject.toml").is_file():
        project_root = candidate
        package_paths.extend(
            str(project_root / component) for component in ("datasets", "datasets/procedural", "models")
        )
    if not any(isinstance(finder, ReasoningGymSourceFinder) for finder in sys.meta_path):
        sys.meta_path.append(ReasoningGymSourceFinder(package_paths, project_root))
