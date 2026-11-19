"""目的：在正式训练前运行并保存与正式任务一致的有界预检。

适用范围：训练分发。隔离预检耗用的随机状态。
"""

from dataclasses import replace

import torch

from .task import PrecheckTask


def automatic_precheck(request):
    devices = [request.device.index or 0] if request.device.type == "cuda" else []
    with torch.random.fork_rng(devices=devices):
        return PrecheckTask().run(replace(request, action="precheck"))
