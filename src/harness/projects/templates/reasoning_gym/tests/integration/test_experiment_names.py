"""Exercise study-name rejection before the writer creates any directory."""

import pytest

from reasoning_gym.run_records import EvaluationRecord, read_run


@pytest.mark.parametrize("study", ["qqzz", "ai_io", "answer_20261126", "answer_12_30", "../answer"])
def test_invalid_experiment_names_leave_no_directory(tmp_path, study):
    with pytest.raises(ValueError):
        EvaluationRecord(tmp_path, "remote_api", "evaluation", study, {})
    assert not (tmp_path / "experiment").exists()


def test_duplicate_experiment_preserves_manifest(tmp_path):
    record = EvaluationRecord(tmp_path, "remote_api", "evaluation", "answer_quality", {})
    previous = record.manifest_path.read_bytes()
    with pytest.raises(FileExistsError):
        EvaluationRecord(tmp_path, "remote_api", "evaluation", "answer_quality", {})
    assert record.manifest_path.read_bytes() == previous


def test_reads_flat_and_managed_result_files(tmp_path):
    flat = tmp_path / "legacy"
    flat.mkdir()
    (flat / "summary.json").write_text('{"total_examples": 1}', encoding="utf-8")
    assert read_run(flat)["summary"]["total_examples"] == 1
    record = EvaluationRecord(tmp_path, "remote_api", "evaluation", "answer_quality", {})
    assert read_run(record.directory)["manifest"]["subname"] == "answer_quality"
