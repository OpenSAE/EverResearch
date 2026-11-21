"""Purpose: Real implementation time-consuming by stage.

Scope of application: precheck, bottleneck analysis and performance comparison. CUDA Phase synchronizing the time boundary.
"""

from contextlib import contextmanager
from time import perf_counter

from ...runtime.config import synchronize


@contextmanager
def timed(stages, name, device):
    synchronize(device)
    start = perf_counter()
    try:
        yield
    finally:
        synchronize(device)
        stages[name] = stages.get(name, 0.0) + perf_counter() - start
