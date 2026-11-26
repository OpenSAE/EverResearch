"""Train the Reasoning Gym GRPO policy with the single-device TRL workflow."""

import argparse
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Optional

import torch
import transformers
from datasets import Dataset as ArrowDataset
from torch.utils.data import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback, set_seed
from transformers.trainer_utils import get_last_checkpoint
from trl import GRPOConfig, GRPOTrainer, ModelConfig, TrlParser

import reasoning_gym
from reasoning_gym.coaching.experiment import Experiment
from reasoning_gym.composite import DatasetSpec
from reasoning_gym.dataset import ProceduralDataset
from reasoning_gym.run_records import EvaluationRecord, write_json
from reasoning_gym.utils import SYSTEM_PROMPTS, extract_answer

from ..precheck.check_training import check_policy


@dataclass
class DatasetConfigItem:
    weight: Optional[float] = field(default=1.0)
    config: Optional[dict] = field(default_factory=dict)


@dataclass
class DatasetConfig:
    dataset_size: int = field(default=10000)
    developer_prompt: str = field(default="DeepSeekZero")
    developer_role: str = field(default="system")
    datasets: dict[str, DatasetConfigItem] = field(default=None)

    def __post_init__(self):
        # Convert dictionary items to DatasetConfigItem instances
        if self.datasets:
            converted_datasets = {}
            for name, config_item in self.datasets.items():
                if isinstance(config_item, dict):
                    converted_datasets[name] = DatasetConfigItem(**config_item)
                else:
                    converted_datasets[name] = config_item
            self.datasets = converted_datasets


class ReasoningGymDataset(Dataset):
    def __init__(
        self,
        tokenizer,
        procedural_dataset: Optional[ProceduralDataset] = None,
        experiment: Optional[Experiment] = None,
        developer_prompt: Optional[str] = None,
        developer_role: Optional[str] = None,
    ):
        self.tokenizer = tokenizer
        self.data = procedural_dataset or experiment.composite
        self.experiment = experiment
        self.developer_prompt = developer_prompt
        self.developer_role = developer_role

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> dict:
        item = self.data[idx]
        question = item["question"]

        chat = []
        if self.developer_role is not None:
            chat.append({"role": self.developer_role, "content": self.developer_prompt})
        chat.append({"role": "user", "content": question})

        prompt = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        return {"prompt": prompt, "item": item}


class CustomGRPOTrainer(GRPOTrainer):
    def __init__(
        self,
        model,
        args: GRPOConfig,
        tokenizer,
        train_dataset: ReasoningGymDataset,
        eval_dataset: ReasoningGymDataset,
    ):
        self.reward_datasets = {"train": train_dataset.data, "validation": eval_dataset.data}
        self.reward_items = {}
        super().__init__(
            model=model,
            reward_funcs=[
                self._accuracy_reward,
                self._format_reward,
            ],
            args=args,
            processing_class=tokenizer,
            train_dataset=self.training_rows(train_dataset, "train"),
            eval_dataset=self.training_rows(eval_dataset, "validation"),
        )

    def training_rows(self, dataset, split):
        items = []
        prompts = []
        for index in range(len(dataset)):
            row = dataset[index]
            items.append(row["item"])
            prompts.append(row["prompt"])
        self.reward_items[split] = items
        return ArrowDataset.from_dict({
            "prompt": prompts, "split": [split] * len(items), "row_index": list(range(len(items))),
        })

    def _accuracy_reward(self, completions: list[str], *, split, row_index, **kwargs) -> list[float]:
        return [
            self.reward_datasets[part].score_answer(extract_answer(completion), self.reward_items[part][index])
            for completion, part, index in zip(completions, split, row_index, strict=True)
        ]

    def _format_reward(self, completions: list[str], **kwargs) -> list[float]:
        def count_tags(text: str) -> float:
            count = 0.0
            if re.search(r"\s*<think>\s*", text):
                count += 0.25
            if re.search(r"\s*</think>\s*", text):
                count += 0.25
            if re.search(r"\s*<answer>\s*", text):
                count += 0.25
            if re.search(r"\s*</answer>\s*", text):
                count += 0.25
            return count

        return [count_tags(c) for c in completions]


def make_dataset(
    tokenizer,
    data_source: Experiment | ProceduralDataset,
    developer_prompt: str,
    developer_role: Optional[str] = None,
) -> ReasoningGymDataset:
    """Create a ReasoningGymDataset from an Experiment or ProceduralDataset."""
    if isinstance(data_source, Experiment):
        return ReasoningGymDataset(
            tokenizer=tokenizer,
            experiment=data_source,
            developer_prompt=developer_prompt,
            developer_role=developer_role,
        )
    else:
        return ReasoningGymDataset(
            tokenizer=tokenizer,
            procedural_dataset=data_source,
            developer_prompt=developer_prompt,
            developer_role=developer_role,
        )


def prepare_datasets(
    config: DatasetConfig,
    tokenizer,
) -> tuple[ReasoningGymDataset, ReasoningGymDataset]:
    """Prepare the training and eval datasets."""
    developer_prompt = SYSTEM_PROMPTS[config.developer_prompt]

    dataset_specs = [
        DatasetSpec(
            name=name,
            weight=ds_config.weight,
            config=ds_config.config,
        )
        for name, ds_config in config.datasets.items()
    ]
    train_data_source = reasoning_gym.create_dataset(
        "composite", seed=1, size=config.dataset_size, datasets=dataset_specs
    )
    val_data_source = reasoning_gym.create_dataset(
        "composite", seed=2, size=config.dataset_size, datasets=dataset_specs
    )
    train_dataset = make_dataset(
        tokenizer=tokenizer,
        data_source=train_data_source,
        developer_prompt=developer_prompt,
        developer_role=config.developer_role,
    )
    eval_dataset = make_dataset(
        tokenizer=tokenizer,
        data_source=val_data_source,
        developer_prompt=developer_prompt,
        developer_role=config.developer_role,
    )
    return train_dataset, eval_dataset


class StepHistory(TrainerCallback):
    """Keep timing of actual completed policy updates and validation passes."""

    def __init__(self, path):
        self.path = path
        self.started = perf_counter()
        self.events = []

    def on_log(self, args, state, control, logs=None, **kwargs):
        event = {"step": state.global_step, "elapsed_seconds": perf_counter() - self.started, "metrics": logs or {}}
        self.events.append(event)
        if self.path is not None:
            write_json(self.path, {"events": self.events})


def main():
    # -----------
    # Parse args
    # -----------
    clock = perf_counter()
    controls = argparse.ArgumentParser(add_help=False)
    controls.add_argument("--precheck", action="store_true")
    controls.add_argument("--study")
    options, arguments = controls.parse_known_args()
    parser = TrlParser((DatasetConfig, GRPOConfig, ModelConfig))
    reasoning_gym_args, training_args, model_args = parser.parse_args_and_config(args=arguments)
    record = None
    if options.study and not options.precheck:
        record = EvaluationRecord(
            Path(__file__).resolve().parents[2], "training_checkpoint", "training", options.study,
            {"dataset": asdict(reasoning_gym_args), "model": asdict(model_args), "training": training_args.to_dict()},
        )
        training_args.output_dir = str(record.directory / "tmp/framework")
    try:
        return train(options, reasoning_gym_args, training_args, model_args, record, clock)
    except KeyboardInterrupt as error:
        if record:
            record.finish("interrupted", error)
        raise
    except Exception as error:
        if record:
            record.finish("failed", error)
        raise


def train(options, reasoning_gym_args, training_args, model_args, record, clock):
    set_seed(training_args.seed)

    # ---------------
    # Set up logging
    # ---------------
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log_level = training_args.get_process_log_level()
    logger.setLevel(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()
    logger.warning(
        f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}"
        + f" distributed training: {bool(training_args.local_rank != -1)}, 16-bits training: {training_args.fp16}"
    )
    logger.info(f"Model parameters {model_args}")
    logger.info(f"Training parameters {training_args}")

    # -----------
    # Load model
    # -----------
    model_clock = perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        torch_dtype=torch.bfloat16,
        attn_implementation=model_args.attn_implementation,
        use_cache=False if training_args.gradient_checkpointing else True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path)
    model_load_seconds = perf_counter() - model_clock

    # --------------------
    # Instantiate trainer
    # --------------------
    training_args.reasoning_gym = reasoning_gym_args
    training_args.remove_unused_columns = False
    train_dataset, eval_dataset = prepare_datasets(reasoning_gym_args, tokenizer)
    model.to(training_args.device)
    report = check_policy(model, tokenizer, train_dataset, eval_dataset)
    report["model_load_seconds"] = model_load_seconds
    precheck_seconds = perf_counter() - clock
    if options.precheck:
        import json

        print(json.dumps(report, indent=2))
        return
    if record:
        record.start(report, precheck_seconds)
    trainer = CustomGRPOTrainer(
        model=model,
        args=training_args,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    # ------------------------------
    # See if we can resume training
    # ------------------------------
    logger.info("Starting training...")
    # Check for last checkpoint
    ckpt = None
    if training_args.resume_from_checkpoint is not None:
        ckpt = training_args.resume_from_checkpoint
    elif os.path.isdir(training_args.output_dir):
        ckpt = get_last_checkpoint(training_args.output_dir)
    if ckpt:
        logger.info(f"\nCheckpoint detected, resuming training at {ckpt=}.")
    else:
        logger.info("\nNo checkpoint detected, starting training from scratch.")

    # ---------------
    # Start training
    # ---------------
    history = StepHistory(record.directory / "reports/progress.json" if record else None)
    trainer.add_callback(history)
    formal_clock = perf_counter()
    train_result = trainer.train(resume_from_checkpoint=ckpt)
    train_metrics = train_result.metrics
    trainer.log_metrics("train", train_metrics)
    trainer.save_metrics("train", train_metrics)
    trainer.save_state()
    if record:
        write_json(record.directory / "reports/timing.json", {
            "model_load_seconds": model_load_seconds, "precheck_seconds": precheck_seconds,
            "formal_seconds": perf_counter() - formal_clock,
            "optimizer_steps": train_result.global_step, "train_rows": len(train_dataset),
            "validation_rows": len(eval_dataset), "metrics": train_metrics,
        })
        record.finish("succeeded")

    # ---------
    # Clean up
    # ---------
    del trainer
    torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
