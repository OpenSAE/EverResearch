"""Exercise the Inspect CLI with local samples and read its saved logs."""

import json
from pathlib import Path

import pytest
from inspect_ai.dataset import MemoryDataset
from inspect_ai.log import list_eval_logs, read_eval_log
from typer.testing import CliRunner

from lighteval import main_inspect
from lighteval.__main__ import app
from lighteval.tasks.registry import Registry


EVAL_ARGS = ["eval", "mockllm/test", "gpqa:diamond", "--max-samples", "1", "--display", "none"]


def test_inspect_default_runs_are_independent_and_readable(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("LIGHTEVAL_WORKSPACE", str(workspace))
    monkeypatch.chdir(tmp_path)

    def local_dataset(path, name, split, sample_fields):
        assert (path, name, split) == ("Idavidrein/gpqa", "gpqa_diamond", "train")
        return MemoryDataset(
            [
                sample_fields(
                    {
                        "Question": question,
                        "Correct Answer": "Paris",
                        "Incorrect Answer 1": "Oslo",
                        "Incorrect Answer 2": "Rome",
                        "Incorrect Answer 3": "Lisbon",
                    }
                )
                for question in ("What is the capital of France?", "Where is the Eiffel Tower?")
            ]
        )

    monkeypatch.setattr(main_inspect, "hf_dataset", local_dataset)

    runner = CliRunner()
    for _ in range(2):
        result = runner.invoke(
            app,
            [*EVAL_ARGS, "--experiment-name", "answer_accuracy", "--frequence-penalty", "0.2"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output

    explicit_dir = Path("previous_layout")
    result = runner.invoke(app, [*EVAL_ARGS, "--log-dir", str(explicit_dir)], catch_exceptions=False)
    assert result.exit_code == 0, result.output

    (model_dir,) = (workspace / "experiment/gpqa").glob("mockllm_test__*")
    runs = model_dir / "diamond_questions/answer_accuracy/runs"
    log_dirs = list(runs.iterdir())
    assert len(log_dirs) == 2
    for log_dir in [*log_dirs, explicit_dir]:
        (log_file,) = list_eval_logs(str(log_dir))
        log = read_eval_log(log_file)
        assert log.status == "success"
        assert log.eval.model == "mockllm/test"
        assert len(log.samples) == 1
        assert log.samples[0].input.startswith("What is the capital of France?")
        assert log.results.total_samples == 1
        penalty = 0.2 if log_dir in log_dirs else None
        assert log.eval.model_generate_config.frequency_penalty == penalty


@pytest.mark.parametrize("name", ["run", "run2", "2026_11_20", "nested/path"])
def test_invalid_experiment_name_is_rejected_before_output(monkeypatch, tmp_path, name):
    monkeypatch.setenv("LIGHTEVAL_WORKSPACE", str(tmp_path))

    result = CliRunner().invoke(app, [*EVAL_ARGS, "--experiment-name", name])

    assert result.exit_code == 2
    assert "answer_accuracy" in result.output
    assert not (tmp_path / "experiment").exists()


def test_inspect_cli_reads_declared_data_file(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    data_file = tmp_path / "samples.jsonl"
    custom_tasks = tmp_path / "local_tasks.py"
    custom_tasks.write_text(
        f"""
from inspect_ai.dataset import Sample
from lighteval.metrics.metrics import Metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig

def sample_fields(record):
    return Sample(input=record["question"], target=record["answer"])

TASKS_TABLE = [LightevalTaskConfig(
    name="local_arithmetic",
    prompt_function=lambda record, task_name: None,
    sample_fields=sample_fields,
    hf_repo="json",
    hf_subset="default",
    hf_data_files={{"train": {str(data_file)!r}}},
    evaluation_splits=["train"],
    metrics=[Metrics.exact_match],
)]
""",
        encoding="utf-8",
    )
    runner = CliRunner()
    for log_name, question, answer in [("original", "What is 2+2?", "4"), ("updated", "What is 3+5?", "8")]:
        data_file.write_text(json.dumps({"question": question, "answer": answer}) + "\n", encoding="utf-8")
        log_dir = tmp_path / log_name
        result = runner.invoke(
            app,
            [
                "eval",
                "mockllm/test",
                "local_arithmetic",
                "--custom-tasks",
                str(custom_tasks),
                "--log-dir",
                str(log_dir),
                "--display",
                "none",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        (log_file,) = list_eval_logs(str(log_dir))
        log = read_eval_log(log_file)
        assert log.status == "success"
        assert [(sample.input, sample.target) for sample in log.samples] == [(question, answer)]


def test_inspect_fewshot_build_does_not_modify_configured_solver(monkeypatch):
    config = Registry(tasks="gsm8k|1").task_to_configs["gsm8k"][0]
    original_solver = config.solver.copy()
    monkeypatch.setattr(
        main_inspect,
        "hf_dataset",
        lambda path, name, split, sample_fields, **kwargs: MemoryDataset(
            [sample_fields({"question": "What is 2+2?", "answer": "#### 4"})]
        ),
    )

    main_inspect.get_inspect_ai_task(config)
    main_inspect.get_inspect_ai_task(config)

    assert config.solver == original_solver


@pytest.mark.parametrize("few_shots_split,expected_split", [(None, "train"), ("validation", "validation")])
def test_inspect_uses_configured_or_inferred_demonstration_split(monkeypatch, few_shots_split, expected_split):
    config = Registry(tasks="gsm8k|1").task_to_configs["gsm8k"][0]
    monkeypatch.setattr(config, "few_shots_split", few_shots_split)
    splits = []

    def local_dataset(path, name, split, sample_fields, **kwargs):
        splits.append(split)
        return MemoryDataset([sample_fields({"question": f"Question from {split}", "answer": "#### 4"})])

    monkeypatch.setattr(main_inspect, "hf_dataset", local_dataset)

    task = main_inspect.get_inspect_ai_task(config)

    assert splits == ["test", expected_split]
    assert [sample.input for sample in task.dataset] == ["Question from test"]


def test_inspect_holds_demonstrations_out_of_single_split(monkeypatch, tmp_path):
    def local_dataset(path, name, split, sample_fields, **kwargs):
        rows = [
            sample_fields(
                {
                    "Question": question,
                    "Correct Answer": "Paris",
                    "Incorrect Answer 1": "Oslo",
                    "Incorrect Answer 2": "Rome",
                    "Incorrect Answer 3": "Lisbon",
                }
            )
            for question in ("What is the capital of France?", "Where is the Eiffel Tower?")
        ]
        return MemoryDataset(rows[: kwargs.get("limit")])

    monkeypatch.setattr(main_inspect, "hf_dataset", local_dataset)

    result = CliRunner().invoke(
        app,
        ["eval", "mockllm/test", "gpqa:diamond|1", "--log-dir", str(tmp_path), "--display", "none"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    (log_file,) = list_eval_logs(str(tmp_path))
    log = read_eval_log(log_file)
    assert log.status == "success"
    assert log.results.total_samples == len(log.samples) == 1
    sample = log.samples[0]
    (demonstration,) = [message.text for message in sample.messages if message.role == "system"]
    assert demonstration.startswith("What is the capital of France?")
    assert sample.input == "Where is the Eiffel Tower?"
