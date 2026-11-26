"""Compatibility entry for nanochat.tokenization.tokenizer."""

import sys
from nanochat.tokenization import tokenizer

sys.modules[__name__] = tokenizer
