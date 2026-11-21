"""Expose the public VGGT package from either a checkout or an installation."""

import sys

from .source_layout import enable_source_layout

sys.modules.setdefault("vggt", sys.modules[__name__])
enable_source_layout()
