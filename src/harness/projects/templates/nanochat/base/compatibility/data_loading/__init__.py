"""Compatibility imports for nanochat.dataloader."""

import sys

from nanochat.climbmix import data_loader

sys.modules[__name__] = data_loader
