"""Check that MTEB's public command applies the selected examples to each task."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


def test_mteb_examples_are_applied_and_reset_between_tasks(tmp_path, monkeypatch):
    pytest.importorskip("faiss")
    pytest.importorskip("pytrec_eval")
    mteb = pytest.importorskip("mteb")
    from FlagEmbedding.evaluation.mteb import MTEBEvalRunner
    from FlagEmbedding.evaluation.mteb.__main__ import main

    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    examples = [{"query": "demonstration query", "response": "demonstration response"}]
    (examples_dir / "ArguAna.json").write_text(json.dumps(examples), encoding="utf-8")
    tasks = [
        SimpleNamespace(metadata=SimpleNamespace(
            name=name, type="Retrieval", main_score="ndcg_at_10", eval_splits=["test"],
        ))
        for name in ("ArguAna", "UnlistedTask")
    ]
    model = SimpleNamespace(
        query_instruction_for_retrieval="Default instruction", examples=None,
        model=SimpleNamespace(config=SimpleNamespace(_name_or_path="local-model")),
        stop_self_pool=lambda: None,
    )
    fallback_examples = [{"query": "fallback", "response": "default response"}]

    def set_examples(override):
        model.examples = fallback_examples if override is None else override

    model.set_examples = set_examples
    seen = []

    class LocalBenchmark:
        def __init__(self, *, tasks):
            self.task = tasks[0]

        def run(self, retriever, *, output_folder, overwrite_results=False):
            assert retriever.embedder is model
            seen.append((
                self.task.metadata.name, model.query_instruction_for_retrieval, model.examples, overwrite_results,
            ))
            result_dir = Path(output_folder) / "no_model_name_available" / "no_revision_available"
            result_dir.mkdir(parents=True, exist_ok=True)
            (result_dir / f"{self.task.metadata.name}.json").write_text(
                json.dumps({"scores": {"test": [{"hf_subset": "default", "main_score": 1.0}]}}), encoding="utf-8"
            )

    monkeypatch.setattr(mteb, "get_tasks", lambda **kwargs: tasks)
    monkeypatch.setattr(mteb, "MTEB", LocalBenchmark)
    monkeypatch.setattr(MTEBEvalRunner, "get_models", staticmethod(lambda args: (model, None)))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "FlagEmbedding.evaluation.mteb", "--embedder_name_or_path", "local-model",
        "--examples_path", str(examples_dir), "--use_special_instructions", "True", "--overwrite", "True",
        "--eval_output_path", "report.json",
    ])

    main()

    assert [task for task, *_ in seen] == ["ArguAna", "UnlistedTask"]
    assert seen[0][1] != "Default instruction"
    assert seen[0][2:] == (examples, True)
    assert seen[1][1:] == ("Default instruction", fallback_examples, True)
    assert json.loads((tmp_path / "report.json").read_text())["Retrieval"]["ArguAna"] == 100.0
