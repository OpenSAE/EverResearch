"""Purpose: Declaration CUB-200 Project portals.

Scope of application: registration, formal classification and pre-checking of data sets.
"""

from .dataset import CLASSES, REQUIRES_ROOT, load, validate_config

__all__ = ["CLASSES", "REQUIRES_ROOT", "SUPPORTED_TASKS", "load", "validate_config"]
SUPPORTED_TASKS = frozenset({"classification"})
