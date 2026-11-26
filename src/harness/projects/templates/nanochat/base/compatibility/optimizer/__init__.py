"""Compatibility imports for nanochat.optim."""

import sys

from tasks.base_training import optimizer

sys.modules[__name__] = optimizer
