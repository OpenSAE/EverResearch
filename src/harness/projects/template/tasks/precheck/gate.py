"""Purpose: Operation and preservation of precheck in line with official tasks prior to formal training.

Scope of application: Training distribution..
"""

from dataclasses import replace

import torch

from .task import PrecheckTask


def automatic_precheck(request):
    devices = [request.device.index or 0] if request.device.type == "cuda" else []
    with torch.random.fork_rng(devices=devices):
        return PrecheckTask().run(replace(request, action="precheck"))
