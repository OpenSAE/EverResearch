"""Compatibility entry for tasks.evaluation.loss_eval."""

import sys
from tasks.evaluation import loss_eval

sys.modules[__name__] = loss_eval
