"""Protect the benchmark data path shared by the CLI and benchmark solver."""

from pathlib import Path

import pytest

from agentflow.precheck.gate import check_benchmark, precheck

DATA = (
    Path(__file__).resolve().parents[1]
    / "assets/prepared_data/benchmark_questions/files/bamboogle/data.json"
)


def test_real_questions_reach_the_precheck():
    summary = precheck(DATA, index=0)
    assert summary["count"] == 125
    assert check_benchmark(DATA, index=0)[0]["query"]


def test_bad_index_is_rejected_before_model_construction():
    with pytest.raises(ValueError, match="outside"):
        precheck(DATA, index=125, model="unavailable-model")
