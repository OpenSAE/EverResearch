"""Check evaluation settings and resolve the policy device before simulator startup."""

from pathlib import Path
from typing import TYPE_CHECKING

from torch import device as TorchDevice

from lerobot.utils.device_utils import get_safe_torch_device

if TYPE_CHECKING:
    from lerobot.configs.eval import EvalPipelineConfig
    from lerobot.configs.policies import PreTrainedConfig


def validate_evaluation(cfg: "EvalPipelineConfig") -> tuple["PreTrainedConfig", Path, TorchDevice]:
    """Return checked evaluation settings and the resolved device."""
    if cfg.policy is None:
        raise ValueError(
            "Evaluation requires a policy: pass --policy.path=<pretrained_dir> or --policy.type=<name>."
        )
    if cfg.policy.device is None:
        # PreTrainedConfig.__post_init__ always resolves the device, so reaching this is a programming error.
        raise ValueError("Policy config has no device set.")
    if cfg.output_dir is None:
        # EvalPipelineConfig.__post_init__ always assigns a default output_dir.
        raise ValueError("EvalPipelineConfig.output_dir is not set.")

    # Check device is available
    resolved_device = get_safe_torch_device(cfg.policy.device, log=True)
    return cfg.policy, cfg.output_dir, resolved_device
