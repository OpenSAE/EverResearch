"""Purpose: Recording of software, equipment and operating settings actually used in the current process.

Scope of application: Environmental sources of precheck, computing and performance results.
"""

from datetime import datetime, timezone
import platform
import sys

import torch
import torchvision


def snapshot(device):
    data = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source": "current_process",
        "python": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "device": str(device),
        "cuda_version": torch.version.cuda,
        "cpu_threads": torch.get_num_threads(),
    }
    if device is not None and device.type == "cuda":
        free, total = torch.cuda.mem_get_info(device)
        data.update(
            gpu=torch.cuda.get_device_name(device),
            available_bytes=free,
            total_bytes=total,
            cudnn=torch.backends.cudnn.version(),
            tf32_matmul=torch.backends.cuda.matmul.allow_tf32,
            tf32_cudnn=torch.backends.cudnn.allow_tf32,
        )
    return data
