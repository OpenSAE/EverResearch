"""Compatibility entry for tasks.evaluation.core_eval."""

import sys
from tasks.evaluation import core_eval

sys.modules[__name__] = core_eval
