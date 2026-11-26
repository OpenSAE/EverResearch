"""Compatibility imports for nanochat.fp8."""

import sys

from nanochat.transformer import float_eight

sys.modules[__name__] = float_eight
