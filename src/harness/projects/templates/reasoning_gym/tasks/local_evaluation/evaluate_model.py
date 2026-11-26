#!/usr/bin/env python

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional

import yaml
from tqdm import tqdm

import reasoning_gym
from reasoning_gym.local_inference.generation import LocalGeneration, TransformersGeneration
from reasoning_gym.run_records import EvaluationRecord, write_json
from reasoning_gym.utils import SYSTEM_PROMPTS, extract_answer

from ..precheck.check_evaluation import check_datasets


@dataclass
class DatasetConfig:
    dataset: str
    size: Optional[int] = None
    seed: Optional[int] = None
    params: Dict[str, Any] = None

    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class CategoryConfig:
    category: str
    datasets: List[DatasetConfig]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CategoryConfig":
        datasets = [DatasetConfig(**d) for d in data["datasets"]]
        return cls(category=data["category"], datasets=datasets)


@dataclass
class EvalConfig:
    model_path: str
    max_tokens: int
    temperature: float
    top_p: float
    save_metadata: bool
    save_full_results: bool
    categories: List[CategoryConfig]
    dtype: str = "auto"
    output_dir: Optional[str] = None
    backend: str = "vllm"

    # Optional: you can provide a system prompt name (looked up in SYSTEM_PROMPTS)
    developer_prompt: Optional[str] = None
    developer_role: str = "system"

    # NEW FIELD: How many times each question is evaluated
    eval_repeats: int = 1

    @classmethod
    def from_yaml(cls, path: str) -> "EvalConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        categories = [CategoryConfig.from_dict(cat) for cat in data["categories"]]
        data["categories"] = categories
        return cls(**data)


def build_dataset(config: DatasetConfig):
    return reasoning_gym.create_dataset(
        config.dataset, **(config.params | {"size": config.size, "seed": config.seed})
    )


class LocalModelEvaluator:
    def __init__(
        self,
        model_path: str,
        config: EvalConfig,
        device: str = "cuda:0",
        batch_size: int = 1,
        verbose: bool = False,
    ):
        self.config = config
        self.device = device
        self.batch_size = batch_size
        self.verbose = verbose

        model_options = (model_path, config.dtype, config.temperature, config.top_p, config.max_tokens)
        if config.backend == "transformers":
            self.model = TransformersGeneration(*model_options, device=device)
        elif config.backend == "vllm":
            self.model = LocalGeneration(*model_options)
        else:
            raise ValueError(f"Unknown local evaluation backend {config.backend!r}")

        self.start_time = datetime.now()
        # If you have a system prompt, retrieve it from SYSTEM_PROMPTS
        self.developer_prompt = None
        if self.config.developer_prompt:
            self.developer_prompt = SYSTEM_PROMPTS[self.config.developer_prompt]
        self.developer_role = self.config.developer_role

    def get_model_response(self, question: str) -> str:
        """
        Generates a single response to the given question and returns the
        raw text of that response.
        """
        # Build a "chat" prompt if developer_prompt is available
        chat = []
        if self.developer_prompt:
            chat.append({"role": self.developer_role, "content": self.developer_prompt})
        chat.append({"role": "user", "content": question})

        response = self.model.generate(chat)

        if self.verbose:
            print(f"[Prompt]\n{question}\n[Response]\n{response}\n{'-'*60}")

        return response

    def process_entry(self, dataset, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate one question from the dataset `eval_repeats` times, then
        average the score. We also keep track of the best (max) score
        and store each completion for potential debugging.
        """
        all_completions = []
        for _ in range(self.config.eval_repeats):
            try:
                raw_response = self.get_model_response(entry["question"])
                model_answer = extract_answer(raw_response)
                score = dataset.score_answer(answer=model_answer, entry=entry)
                score = 0.0 if score < 1 else score
                all_completions.append(
                    {
                        "model_answer": model_answer,
                        "full_model_response": raw_response,
                        "score": score,
                    }
                )
            except Exception as e:
                # If there's an error on a single repetition, store it and continue
                all_completions.append(
                    {
                        "model_answer": None,
                        "full_model_response": "",
                        "score": 0.0,
                        "error": str(e),
                    }
                )

        # Compute statistics across all runs
        scores = [c["score"] for c in all_completions]
        mean_score = sum(scores) / len(scores)
        best_score = max(scores)

        return {
            "question": entry["question"],
            "expected_answer": str(entry["answer"]),
            "best_score": best_score,
            "mean_score": mean_score,
            "completions": all_completions,
        }

    def evaluate_dataset(self, category_name: str, dataset_config: DatasetConfig) -> Dict[str, Any]:
        """
        Loads the dataset, processes each entry, and then computes
        the overall average across all entries.
        """
        dataset_name = dataset_config.dataset
        params = dataset_config.params | {"size": dataset_config.size, "seed": dataset_config.seed}
        dataset = build_dataset(dataset_config)
        entries = list(dataset)

        results = []
        for entry in tqdm(entries, desc=f"Processing {dataset_name}"):
            results.append(self.process_entry(dataset, entry))

        # Summarize the entire dataset
        total_mean_score = sum(r["mean_score"] for r in results)
        avg_score = total_mean_score / len(results) if results else 0.0

        return {
            "name": dataset_name,
            "category": category_name,
            "average_score": avg_score,
            "total_examples": len(results),
            "config": params,
            "results": results,
        }

    def evaluate_all(self) -> Dict[str, Any]:
        """
        Runs evaluation on all categories/datasets.
        """
        cat_results = []
        for cat in self.config.categories:
            datasets = []
            for ds_cfg in cat.datasets:
                datasets.append(self.evaluate_dataset(cat.category, ds_cfg))
            cat_results.append({"name": cat.category, "datasets": datasets})

        return {
            "metadata": {
                "timestamp": self.start_time.isoformat(),
                "model": self.config.model_path,
                "device": self.device,
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "dtype": self.config.dtype,
                "top_p": self.config.top_p,
                "eval_repeats": self.config.eval_repeats,
            },
            "categories": cat_results,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--study", default="answer_quality")
    parser.add_argument("--backend", choices=("transformers", "vllm"))
    parser.add_argument("--output-dir")
    parser.add_argument("--category")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")

    parser.add_argument("--precheck", action="store_true", help="Load the selected model and score one generated response")
    args = parser.parse_args()

    # Load config from YAML
    config = EvalConfig.from_yaml(args.config)

    # Command-line overrides
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.backend:
        config.backend = args.backend
    if args.category:
        # Filter categories if specified
        config.categories = [c for c in config.categories if c.category == args.category]
        if not config.categories:
            print(f"Category '{args.category}' not found.")
            return 1

    record = None
    clock = perf_counter()
    try:
        if not (args.precheck or args.output_dir):
            record = EvaluationRecord(
                Path(__file__).resolve().parents[2], "local_inference", "local_evaluation",
                args.study, {**asdict(config), "device": args.device, "batch_size": args.batch_size},
            )
        checked = check_datasets(config.categories, build_dataset)
        load_clock = perf_counter()
        evaluator = LocalModelEvaluator(
            model_path=config.model_path,
            config=config,
            device=args.device,
            batch_size=args.batch_size,
            verbose=args.verbose,
        )
        model_load_seconds = perf_counter() - load_clock
        dataset = build_dataset(config.categories[0].datasets[0])
        entry = dataset[0]
        model_clock = perf_counter()
        response = evaluator.get_model_response(entry["question"])
        if not isinstance(response, str) or not response.strip():
            raise ValueError("The model returned an empty completion")
        report = {
            "datasets": checked, "samples_checked": 1, "model": config.model_path, "model_called": True,
            "model_score": dataset.score_answer(extract_answer(response), entry),
            "model_load_seconds": model_load_seconds,
            "model_response_seconds": perf_counter() - model_clock,
        }
        precheck_seconds = perf_counter() - clock
        if args.precheck:
            print(json.dumps(report, indent=2))
            return 0

        if record:
            record.start(report, precheck_seconds)
        formal_clock = perf_counter()
        results = evaluator.evaluate_all()
        datasets = [dataset for category in results["categories"] for dataset in category["datasets"]]
        count = sum(dataset["total_examples"] for dataset in datasets)
        failed = sum(
            "error" in completion
            for dataset in datasets for entry in dataset["results"] for completion in entry["completions"]
        )
        output = (
            record.directory / "artifacts/results.json" if record else Path(args.output_dir) / "results.json"
        )
        write_json(output, results)
        if record:
            write_json(record.directory / "reports/timing.json", {
                "precheck_seconds": precheck_seconds, "model_load_seconds": model_load_seconds,
                "formal_seconds": perf_counter() - formal_clock, "samples_completed": count,
                "completions_per_prompt": config.eval_repeats, "batch_size": 1,
            })
        if not count or failed:
            raise RuntimeError(f"Evaluation finished {count} prompts with {failed} failed completions.")
        if record:
            record.finish("succeeded")
        print(f"Results saved to {output}")
        return 0
    except KeyboardInterrupt as error:
        if record:
            record.finish("interrupted", error)
        raise
    except Exception as error:
        if record:
            record.finish("failed", error)
        print(f"Error during local evaluation: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
