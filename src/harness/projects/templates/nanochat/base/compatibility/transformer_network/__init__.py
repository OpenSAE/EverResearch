"""Compatibility imports for nanochat.gpt."""

import sys

from nanochat.transformer import network

sys.modules[__name__] = network
