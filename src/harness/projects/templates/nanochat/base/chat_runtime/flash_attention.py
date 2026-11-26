"""Compatibility entry for nanochat.transformer.flash_attention."""

import sys
from nanochat.transformer import flash_attention

sys.modules[__name__] = flash_attention
