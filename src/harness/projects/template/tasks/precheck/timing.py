"""目的：按阶段测量真实执行耗时。

适用范围：预检、瓶颈分析和性能候选比较。CUDA 阶段在计时边界同步。
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
