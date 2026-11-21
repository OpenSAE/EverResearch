"""Check how Pipeline studies locate saved results and response details."""

import json
from pathlib import Path

import pytest
from datasets import Dataset
from typer.testing import CliRunner

from lighteval.__main__ import app
from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.logging.run_paths import study_directory
from lighteval.models.dummy.dummy_model import DummyModel, DummyModelConfig
from lighteval.models.model_output import ModelResponse
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.tasks.requests import SamplingMethod
from lighteval.utils.cache_management import cached


def test_study_reads_selected_task_details(monkeypatch, tmp_path):
    monkeypatch.setenv("LIGHTEVAL_WORKSPACE", str(tmp_path / "workspace"))
    monkeypatch.chdir(tmp_path)
    tracker = EvaluationTracker(output_dir=None, experiment_name="answer_scoring")
    tracker.set_experiment_location(["truthfulqa/truthful_qa"], ["openai-community/gpt2"], ["truthfulqa:mc|0"])
    dataset = Dataset.from_list([{"value": "first"}])
    tracker.save_results("first_timestamp", {})
    tracker.save_details("first_timestamp", {"truthfulqa:mc|0": dataset})
    tracker.save_details("second_timestamp", {"truthfulqa:mc|0": dataset, "another_task|0": dataset})

    study = Path("workspace/experiment/truthful_qa/gpt2_transformer/multiple_choice/answer_scoring")
    assert (study / "results/results_first_timestamp.json").is_file()
    assert len(list((study / "details").iterdir())) == 2
    assert tracker.load_details_datasets("first", ["truthfulqa:mc|0"])["truthfulqa:mc|0"][0] == dataset[0]
    latest = tracker.load_details_datasets("last", ["truthfulqa:mc|0"])
    assert list(latest) == ["truthfulqa:mc|0"]
    assert latest["truthfulqa:mc|0"][0] == dataset[0]


def test_study_replays_old_layout_and_skips_other_fewshot_counts(monkeypatch, tmp_path):
    monkeypatch.setenv("LIGHTEVAL_WORKSPACE", str(tmp_path))
    tracker = EvaluationTracker(output_dir=None)
    tracker.set_experiment_location(["openai/gsm8k"], ["model"], ["gsm8k|0"])
    tracker.save_details("2026-11-20", {"gsm8k|0": Dataset.from_list([{"value": "zero shot"}])})
    old_run = tmp_path / "experiment/openai~2Fgsm8k/model/gsm8k~7C0/benchmark_evaluation/details/2026-11-19"
    old_run.mkdir(parents=True)
    Dataset.from_list([{"value": "old layout"}]).to_parquet(old_run / "details_gsm8k|0_2026-11-19.parquet")

    fewshot_tracker = EvaluationTracker(output_dir=None)
    fewshot_tracker.set_experiment_location(["openai/gsm8k"], ["model"], ["gsm8k|5"])
    assert fewshot_tracker.output_dir == tracker.output_dir
    fewshot_tracker.save_details("2026-11-21", {"gsm8k|5": Dataset.from_list([{"value": "five shot"}])})

    assert tracker.load_details_datasets("last", ["gsm8k|0"])["gsm8k|0"][0]["value"] == "zero shot"
    assert tracker.load_details_datasets("first", ["gsm8k|0"])["gsm8k|0"][0]["value"] == "old layout"
    assert tracker.load_details_datasets("2026-11-19", ["gsm8k|0"])["gsm8k|0"][0]["value"] == "old layout"


def test_study_names_preserve_distinct_sources_and_task_selections(monkeypatch, tmp_path):
    monkeypatch.setenv("LIGHTEVAL_WORKSPACE", str(tmp_path))
    namespaced = study_directory(["org/data"], ["model"], ["first|0", "second|0"], "answer_scoring")
    reordered = study_directory(["org/data"], ["model"], ["second|2", "first|1", "first|2"], "answer_scoring")
    plain = study_directory(["org_data"], ["model"], ["first|0", "second|0"], "answer_scoring")

    assert namespaced == reordered
    assert namespaced != plain
    assert namespaced.relative_to(tmp_path).parts[1].startswith("org_data__")
    assert namespaced.parent.name.startswith("first_and_second__")


def test_accelerate_rejects_generic_study_name_before_loading(monkeypatch, tmp_path):
    monkeypatch.setenv("LIGHTEVAL_WORKSPACE", str(tmp_path / "workspace"))
    result = CliRunner().invoke(
        app,
        ["accelerate", "model_name=unavailable", "unknown_task", "--experiment-name", "run2"],
    )
    assert result.exit_code == 2, result.output
    assert "answer_accuracy" in result.output
    assert not (tmp_path / "workspace" / "experiment").exists()


def test_explicit_filesystem_reads_saved_details(tmp_path):
    tracker = EvaluationTracker(output_dir=f"memory://{tmp_path.name}")
    tracker.general_config_logger.model_name = "org/model"
    dataset = Dataset.from_list([{"value": "saved", "choices": ["a", "b"]}])
    tracker.save_details("saved_timestamp", {"task|0": dataset})

    restored = tracker.load_details_datasets("last", ["task|0"])["task|0"]

    assert restored[:] == dataset[:]
    assert restored.features == dataset.features


def test_baseline_cli_loads_multiple_local_tasks_in_parallel(tmp_path):
    for task_name, choices in [("binary", ["yes", "no"]), ("ternary", ["red", "green", "blue"])]:
        sample = {"question": f"Choose from {choices}", "choices": choices}
        (tmp_path / f"{task_name}.jsonl").write_text(json.dumps(sample) + "\n", encoding="utf-8")

    custom_tasks = tmp_path / "local_baseline_tasks.py"
    custom_tasks.write_text(
        f"""
from pathlib import Path

from lighteval.metrics.metrics import Metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

def prompt(item, task_name):
    return Doc(query=item["question"], choices=item["choices"], gold_index=0, task_name=task_name)

TASKS_TABLE = [LightevalTaskConfig(
    name=name,
    prompt_function=prompt,
    hf_repo="json",
    hf_subset="default",
    hf_data_files=str(Path({str(tmp_path)!r}) / f"{{name}}.jsonl"),
    evaluation_splits=["train"],
    metrics=[Metrics.loglikelihood_acc],
) for name in ("binary", "ternary")]
""",
        encoding="utf-8",
    )
    runner = CliRunner()
    expected_scores = {"binary|0": 0.5, "ternary|0": 1 / 3}
    for workers in (1, 2):
        output = tmp_path / f"workers_{workers}"
        result = runner.invoke(
            app,
            [
                "baseline",
                "binary,ternary",
                "--custom-tasks",
                str(custom_tasks),
                "--dataset-loading-processes",
                str(workers),
                "--output-dir",
                str(output),
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        (summary,) = output.glob("results/baseline/results_*.json")
        task_scores = json.loads(summary.read_text(encoding="utf-8"))["results"]
        assert {task: task_scores[task]["acc"] for task in expected_scores} == expected_scores


def test_pipeline_applies_recipe_before_evaluation_and_reads_back(monkeypatch, tmp_path):
    monkeypatch.setenv("LIGHTEVAL_WORKSPACE", str(tmp_path))
    data_file = tmp_path / "samples.jsonl"
    data_file.write_text(json.dumps({"question": "What is 2+2?", "answer": "4"}) + "\n")
    custom_tasks = tmp_path / "local_tasks.py"
    custom_tasks.write_text(
        f"""
from lighteval.metrics.metrics import Metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

def prompt(item, task_name):
    return Doc(query=item["question"], choices=[item["answer"]], gold_index=0, task_name=task_name)

TASKS_TABLE = [LightevalTaskConfig(
    name="local_arithmetic",
    prompt_function=prompt,
    hf_repo="json",
    hf_subset="default",
    hf_data_files={str(data_file)!r},
    evaluation_splits=["train"],
    metrics=[Metrics.exact_match],
)]
"""
    )
    recipe = tmp_path / "model.yaml"
    recipe.write_text(
        f"model_parameters:\n  cache_dir: {tmp_path / 'cache'}\nmetric_options:\n  em:\n    num_samples: 3\n"
    )
    config, metric_options = DummyModelConfig.from_path_with_metric_options(str(recipe))

    class LocalModel(DummyModel):
        model_calls = []

        @cached(SamplingMethod.GENERATIVE)
        def greedy_until(self, docs):
            self.model_calls.extend(doc.num_samples for doc in docs)
            return [ModelResponse(text=["4"] * doc.num_samples) for doc in docs]

    model = LocalModel(config)

    def pipeline(options, experiment_name="answer_scoring", readback=None):
        return Pipeline(
            tasks="local_arithmetic",
            pipeline_parameters=PipelineParameters(
                launcher_type=ParallelismManager.NONE,
                custom_tasks_directory=str(custom_tasks),
                load_responses_from_details_date_id=readback,
            ),
            evaluation_tracker=EvaluationTracker(output_dir=None, experiment_name=experiment_name),
            model=model,
            metric_options=options,
        )

    pipeline(options=None, experiment_name="single_answer").evaluate_and_save()
    original = pipeline(options=metric_options)
    results = original.evaluate_and_save()["results"]
    study = tmp_path / "experiment/json/dummy/local_arithmetic/answer_scoring"
    (summary,) = (study / "executions").glob("*/artifacts/scores.json")
    assert json.loads(summary.read_text())["results"]["local_arithmetic|0"]["em"] == 1

    replay = pipeline(options=metric_options, readback="last")
    replay.evaluate()
    assert replay.get_results()["results"] == results

    with pytest.raises(ValueError, match="different generation count"):
        pipeline(options=None, readback="last").evaluate()
    assert model.model_calls == [1, 3]
