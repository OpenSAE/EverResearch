"""Test saved-run validation through the public CLI.

The fixture uses small generated records to cover migration errors without
requiring a trained model or research data.
"""


import json
from pathlib import Path
import shutil

import yaml

from harness.cli import main


TEMPLATE = Path(__file__).resolve().parents[1] / "projects/template"


def prepare_saved_runs(root):
    shutil.copytree(TEMPLATE, root, ignore=shutil.ignore_patterns(".*", "__pycache__"))
    for study, run_id in (
        ("scratch_baseline", "20261119T013844Z-baseline"),
        ("imagenet_finetune", "20261119T014957Z-finetune"),
        ("offline_check", "20261119T022754Z-offline"),
    ):
        run = root / "experiment/cub200/resnet18_mlp/classification" / study / run_id
        config = {
            "dataset": {"name": "cub200"},
            "model": {"name": "resnet18_mlp"},
            "task": {"name": "classification"},
        }
        outputs = {
            "model": "artifacts/model.pt",
            "evaluation": "reports/evaluation.json",
            "precheck": "reports/precheck.json",
        }
        manifest = {
            "effective_config": "config.yaml",
            "configuration": config,
            "run_id": run_id,
            "subname": study,
            "status": "succeeded",
            "outputs": outputs,
        }
        (run / "metadata").mkdir(parents=True)
        (run / "artifacts").mkdir()
        (run / "reports").mkdir()
        (run / "config.yaml").write_text(yaml.safe_dump(config))
        (run / "metadata/manifest.json").write_text(json.dumps(manifest))
        (run / outputs["model"]).write_bytes(b"fixture")
        (run / outputs["evaluation"]).write_text('{"accuracy": 0.5}')
        (run / outputs["precheck"]).write_text('{"samples_checked": 4}')


def test_experiment_check_accepts_saved_runs_and_detects_migration_errors(tmp_path, capsys):
    root = tmp_path / "BirdClassification"
    prepare_saved_runs(root)
    command = ["projects", "experiment", "check", str(root)]

    assert main(command) == 0
    assert json.loads(capsys.readouterr().out)["runs"] == 3

    study = root / "experiment/cub200/resnet18_mlp/classification/scratch_baseline"
    run = next(path for path in study.iterdir() if path.is_dir())
    model = run / "artifacts/model.pt"
    model.rename(model.with_name("saved_model.pt"))
    config = run / "config.yaml"
    config.write_text(config.read_text().replace("name: resnet18_mlp", "name: small_cnn"))
    historical = study.with_name("historical_results") / "artifacts"
    historical.mkdir(parents=True)
    shutil.copyfile(run / "reports/evaluation.json", historical / "evaluation.json")

    assert main(["projects", "layout", "check", str(root)]) == 1
    assert {item["rule"] for item in json.loads(capsys.readouterr().out)["violations"]} == {"name_english_word"}
    assert main(command) == 1
    report = json.loads(capsys.readouterr().out)
    assert {item["rule"] for item in report["violations"]} == {
        "config_mismatch", "output_unlisted", "output_missing", "run_identity", "run_manifest",
    }

    model.with_name("saved_model.pt").rename(model)
    manifest_path = run / "metadata/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["outputs"]["model"] = "artifacts/other_model.pt"
    manifest_path.write_text(json.dumps(manifest))
    assert main(command) == 1
    assert "output_name" in {item["rule"] for item in json.loads(capsys.readouterr().out)["violations"]}


def test_precheck_check_uses_valid_runs_and_requires_failed_gate_to_block(tmp_path, capsys):
    root = tmp_path / "project"
    prepare_saved_runs(root)
    results = root / "experiment/cub200/resnet18_mlp/classification"
    passed = next(path for path in (results / "scratch_baseline").iterdir() if path.is_dir())
    rejected = next(path for path in (results / "imagenet_finetune").iterdir() if path.is_dir())
    passed_path = passed / "metadata/manifest.json"
    rejected_path = rejected / "metadata/manifest.json"
    success_record = json.loads(passed_path.read_text())
    success_record.update(formal_started=True, precheck_seconds=2.5)
    passed_path.write_text(json.dumps(success_record))
    precheck_report = passed / success_record["outputs"]["precheck"]
    precheck_report.write_text(json.dumps({"samples_checked": 4}))

    failure_record = json.loads(rejected_path.read_text())
    for filename in failure_record["outputs"].values():
        (rejected / filename).unlink()
    failure_record.update(
        formal_started=False,
        status="failed",
        outputs={},
        diagnostics=[{"stage": "automatic_precheck", "message": "Incompatible input shape"}],
    )
    rejected_path.write_text(json.dumps(failure_record))

    command = [
        "projects", "precheck", "check", str(root), str(passed), str(rejected),
        "--max-samples", "4",
    ]
    assert main([*command, "--max-seconds", "3"]) == 0
    assert json.loads(capsys.readouterr().out)["violations"] == []

    failure_record["formal_started"] = True
    rejected_path.write_text(json.dumps(failure_record))
    assert main([*command, "--max-seconds", "2"]) == 1
    assert {item["rule"] for item in json.loads(capsys.readouterr().out)["violations"]} == {
        "precheck_duration", "precheck_blocking",
    }

    precheck_report.write_text(json.dumps({"samples_checked": 5}))
    assert main([*command, "--max-seconds", "3"]) == 1
    assert "precheck_samples" in {
        item["rule"] for item in json.loads(capsys.readouterr().out)["violations"]
    }

    precheck_report.unlink()
    assert main([*command, "--max-seconds", "3"]) == 1
    assert "output_missing" in {
        item["rule"] for item in json.loads(capsys.readouterr().out)["violations"]
    }
