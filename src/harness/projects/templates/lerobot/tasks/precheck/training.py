"""Validate training options before workers or accelerator processes start."""

import datetime as dt
import logging
import multiprocessing
from pathlib import Path
from typing import TYPE_CHECKING

from lerobot.configs.default import PeftConfig

if TYPE_CHECKING:
    from lerobot.configs.train import TrainPipelineConfig


def validate_training(cfg: "TrainPipelineConfig") -> None:
    """Resolve and check a training configuration before opening its dataset."""
    available_contexts = multiprocessing.get_all_start_methods()
    if (
        cfg.dataloader_multiprocessing_context is not None
        and cfg.dataloader_multiprocessing_context not in available_contexts
    ):
        raise ValueError(
            "`dataloader_multiprocessing_context` must be None or one of "
            f"{available_contexts} on this platform, got "
            f"{cfg.dataloader_multiprocessing_context!r}."
        )

    cfg._resolve_pretrained_from_cli()

    if cfg.policy is None and cfg.reward_model is None:
        raise ValueError(
            "Neither policy nor reward_model is configured. "
            "Please specify one with `--policy.path` or `--reward_model.path`."
        )

    active_cfg = cfg.trainable_config

    # `--peft.*` and `--policy.use_peft=true` both request PEFT training: normalize them so that
    # `make_policy` and the training loop see the same thing.
    if cfg.policy is not None and (cfg.peft is not None or cfg.policy.use_peft):
        if cfg.policy.pretrained_path is None and not cfg.resume:
            raise ValueError(
                "Training from scratch using PEFT is unlikely to yield good results. "
                "Supply a `--policy.path` to fine-tune an existing model."
            )
        cfg.policy.use_peft = True
        if cfg.peft is None:
            logging.info(
                "`policy.use_peft=true` without `--peft.*` options: using the default PEFT config."
            )
            cfg.peft = PeftConfig()

    if cfg.rename_map and active_cfg.pretrained_path is None and not cfg.resume:
        raise ValueError(
            "`rename_map` requires a pretrained policy checkpoint. "
            "Fresh initialization derives feature names from the current dataset, so no rename is applied."
        )

    if not cfg.job_name:
        if cfg.env is None:
            cfg.job_name = f"{active_cfg.type}"
        else:
            cfg.job_name = f"{cfg.env.type}_{active_cfg.type}"

    if not cfg.resume and isinstance(cfg.output_dir, Path) and cfg.output_dir.is_dir():
        raise FileExistsError(
            f"Output directory {cfg.output_dir} already exists and resume is {cfg.resume}. "
            f"Please change your output directory so that {cfg.output_dir} is not overwritten."
        )
    elif not cfg.output_dir:
        now = dt.datetime.now()
        train_dir = f"{now:%Y-%m-%d}/{now:%H-%M-%S}_{cfg.job_name}"
        cfg.output_dir = Path("outputs/train") / train_dir

    if isinstance(cfg.dataset.repo_id, list):
        raise NotImplementedError("LeRobotMultiDataset is not currently implemented.")

    if not cfg.use_policy_training_preset and (cfg.optimizer is None or cfg.scheduler is None):
        raise ValueError("Optimizer and Scheduler must be set when the policy presets are not used.")
    elif cfg.use_policy_training_preset and not cfg.resume:
        cfg.optimizer = active_cfg.get_optimizer_preset()
        cfg.scheduler = active_cfg.get_scheduler_preset()

    image_transforms = cfg.dataset.image_transforms
    if image_transforms.enable and image_transforms.backend == "gpu" and active_cfg.device == "cpu":
        raise ValueError(
            "dataset.image_transforms.backend='gpu' needs an accelerator device, but policy.device is 'cpu'. "
            "Use image_transforms.backend='dataloader' to augment in the DataLoader workers."
        )

    if cfg.eval_steps > 0 and cfg.dataset.eval_split == 0.0:
        raise ValueError("eval_steps > 0 requires dataset.eval_split > 0.0 to hold out eval data.")

    # Remote runs auto-generate the repo_id in submit_to_hf (the policy may only be
    # resolved here, from --policy.path), so don't demand it up front for them.
    if (
        hasattr(active_cfg, "push_to_hub")
        and active_cfg.push_to_hub
        and not active_cfg.repo_id
        and not cfg.job.is_remote
    ):
        raise ValueError("'repo_id' argument missing. Please specify it to push the model to the hub.")

    if cfg.save_checkpoint_to_hub and not (cfg.policy is not None and cfg.policy.repo_id):
        raise ValueError("save_checkpoint_to_hub requires --policy.repo_id.")

    cfg._validate_distributed()

