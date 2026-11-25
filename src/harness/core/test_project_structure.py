"""Verify that the central project check rejects typical macro-structure leakages.

Check the quarantine catalogue and reference project layout by normal order, distinguishing the subdivision path from the overall acceptance.
"""

import json
from pathlib import Path
import shutil

from harness.cli import main


TEMPLATE = Path(__file__).resolve().parents[1] / "projects/templates/cub"


def write(root, relative, source):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def test_project_check_requires_real_components_and_counts_deep_files(tmp_path, capsys):
    root = tmp_path / "ContextMemory"
    write(root, "base/memory/runtime.py", "def dispatch(task):\n    return task()\n")
    write(root, "base/memory/models/encoder.py", "def encode(value):\n    return value + 1\n")
    write(root, "tasks/precheck/task.py", "def precheck(task):\n    return task()\n")
    write(root, "models/encoder/model.py", "def encode(value):\n    return None\n")
    write(root, "conf/config.yaml", "# only a comment\n")
    for number in range(16):
        write(root, f"scripts/analysis/summary/{number}.md", "")

    assert main(["projects", "project", "check", str(root)]) == 1
    result = json.loads(capsys.readouterr().out)
    reported = {(item["path"], item["rule"]) for item in result["violations"]}
    assert {
        ("datasets", "required_directory"),
        ("models", "component_implementation"),
        ("tasks", "component_implementation"),
        ("conf", "configuration_entry"),
        ("base/memory/models", "nested_component"),
        ("scripts/analysis/summary", "directory_file_count"),
    } <= reported


def test_reference_component_split_passes_project_check(tmp_path, capsys):
    root = tmp_path / "ImageClassification"
    shutil.copytree(
        TEMPLATE, root, ignore=shutil.ignore_patterns(".*", "__pycache__", "experiment")
    )
    assert main(["projects", "layout", "check", str(root)]) == 0
    baseline = json.loads(capsys.readouterr().out)
    assert main(["projects", "project", "check", str(root)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["violations"] == baseline["violations"]
    assert result["components"] == {
        "dataset": ["cub200"], "model": ["convolution", "residual"], "task": ["classification"],
    }


def test_project_check_accepts_structured_project(tmp_path, capsys):
    root = tmp_path / "ContextMemory"
    write(root, "base/memory/runtime.py", "def dispatch(task):\n    return task()\n")
    write(root, "datasets/corpus/dataset.py", "def read(source):\n    return source.read()\n")
    write(root, "models/encoder/model.py", "def encode(value):\n    return value + 1\n")
    write(root, "tasks/embedding/task.py", "def evaluate(data, model):\n    return model(data)\n")
    write(root, "tasks/precheck/task.py", "def precheck(task):\n    return task()\n")
    write(root, "conf/config.yaml", "task: embedding\n")
    assert main(["projects", "project", "check", str(root)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert {entry["rule"] for entry in result["violations"]} == {
        "environment_documentation", "environment_navigation",
    }
    write(root, "doc/environment/README.md", "# Environment\n")
    write(root, "doc/README.md", "[Environment](environment/README.md)\n")
    assert main(["projects", "project", "check", str(root)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert [entry["rule"] for entry in result["violations"]] == ["environment_documentation"]
    write(root, "doc/environment/README.md", "# Environment\n\nUse the chosen interpreter.\n")
    assert main(["projects", "project", "check", str(root)]) == 0
    assert json.loads(capsys.readouterr().out)["passed"]

    for name in ("alpha", "beta", "gamma", "delta", "epsilon", "zeta",
                 "eta", "theta", "iota", "kappa", "lambda", "mu", "nu",
                 "xi", "omicron", "pi"):
        (root / "scripts" / name).mkdir(parents=True, exist_ok=True)
    assert main(["projects", "project", "check", str(root)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["violations"] == []
    assert [(item["path"], item["files"], item["directories"])
            for item in result["directory_reviews"]] == [("scripts", 0, 16)]

    example = root / "scripts/example"
    example.mkdir()
    for name in ("alpha", "beta"):
        (root / "scripts" / name).rename(example / name)
    assert main(["projects", "project", "check", str(root)]) == 0
    assert json.loads(capsys.readouterr().out)["directory_reviews"] == []


def test_project_count_checks_legacy_python_package(tmp_path, capsys):
    root = tmp_path / "ContextMemory"
    write(root, "memory/__init__.py", "")
    for number in range(16):
        write(root, f"memory/runtime/module_{number}.py", "")
    assert main(["projects", "project", "check", str(root)]) == 1
    reported = {(item["path"], item["rule"])
                for item in json.loads(capsys.readouterr().out)["violations"]}
    assert ("memory", "root_directory") in reported
    assert ("memory/runtime", "directory_file_count") in reported


def test_project_count_exempts_data_and_model_subtrees(tmp_path, capsys):
    root = tmp_path / "ContextMemory"
    write(root, "datasets/corpus/dataset.py", "def read(source):\n    return source.read()\n")
    write(root, "models/encoder/model.py", "def encode(value):\n    return value + 1\n")
    for number in range(16):
        for component in ("datasets/corpus", "models/encoder", "scripts/analysis"):
            write(root, f"{component}/support_{number}.py", "")
            (root / component / f"group_{number}").mkdir()

    assert main(["projects", "project", "check", str(root)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["components"]["dataset"] == ["corpus"]
    assert result["components"]["model"] == ["encoder"]
    assert [item["path"] for item in result["violations"]
            if item["rule"] == "directory_file_count"] == ["scripts/analysis"]
    assert [item["path"] for item in result["directory_reviews"]] == ["scripts/analysis"]

    (root / "scripts/analysis/support_15.py").unlink()
    (root / "scripts/analysis/group_15").rmdir()
    assert main(["projects", "project", "check", str(root)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert all(item["rule"] != "directory_file_count" for item in result["violations"])
    assert result["directory_reviews"] == []


def test_experiment_paths_use_catalogs_from_supported_configuration_formats(tmp_path, capsys):
    for suffix, config in {
        "json": '{"catalogs": {"dataset": {"sample_corpus": {}}}}',
        "toml": "[catalogs.dataset.sample_corpus]\n",
    }.items():
        root = tmp_path / suffix / "ContextMemory"
        write(root, f"conf/config.{suffix}", config)
        (root / "experiment/sample_corpus").mkdir(parents=True)
        assert main(["projects", "layout", "check", str(root)]) == 0
        assert json.loads(capsys.readouterr().out)["passed"]
