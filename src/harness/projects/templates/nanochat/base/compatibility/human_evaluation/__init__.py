import sys

from tasks.conversation import human_evaluation

sys.modules[__name__] = human_evaluation
