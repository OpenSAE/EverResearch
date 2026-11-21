# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

# flake8: noqa
import sys

from . import text_helpers
from .tasks.compression import prompt_compressor
from .version import VERSION as __version__

__all__ = ["PromptCompressor"]

# Preserve the import paths used by existing library consumers.
sys.modules[f"{__name__}.utils"] = utils = text_helpers
sys.modules[f"{__name__}.prompt_compressor"] = prompt_compressor
PromptCompressor = prompt_compressor.PromptCompressor
PromptCompressor.__module__ = f"{__name__}.prompt_compressor"
