"""Validation of normal access and non-compliant path exit status for central layout check.

Use Real CUB A copy of the reference item isolated from it, covering the various directories and project-specific names.
"""

import json
from pathlib import Path
import shutil

from harness.cli import main


TEMPLATE = Path(__file__).resolve().parents[1] / "projects/templates/cub"


def check(root, capsys, status):
    assert main(["projects", "layout", "check", str(root)]) == status
    report = json.loads(capsys.readouterr().out)
    assert report["project"] == str(root.resolve())
    assert report["passed"] is (status == 0)
    return report


def test_layout_preserves_names_inside_upstream_packages(capsys, tmp_path):
    root = tmp_path / "ContextMemory"
    for relative in ("python/__init__.py", "app/(home)/+page.ts"):
        path = root / "third_party/upstream" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    check(root, capsys, 0)

    (root / "third_party/+loose.py").touch()
    violations = check(root, capsys, 1)["violations"]
    assert {item["path"] for item in violations} == {"third_party/+loose.py"}


def test_layout_accepts_documentation_build_sources_under_named_site(capsys, tmp_path):
    root = tmp_path / "ContextMemory"
    site = root / "doc/code/reference"
    for relative in ("Makefile", "source/conf.py", "source/API/PublicModule.rst",
                     "source/_static/OriginalLogo.png"):
        path = site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    check(root, capsys, 0)

    (root / "doc/Unowned.rst").touch()
    violations = check(root, capsys, 1)["violations"]
    assert {item["path"] for item in violations} == {"doc/Unowned.rst"}


def test_layout_preserves_original_paths_inside_historical_runs(capsys, tmp_path):
    root = tmp_path / "ContextMemory"
    archive = root / "assets/history_experiment/archived_results"
    original = archive / "files/A0_1/S1 (baseline)/TrainRun.py"
    original.parent.mkdir(parents=True)
    original.touch()
    readme = archive / "README.md"
    readme.touch()
    check(root, capsys, 0)

    readme.unlink()
    outside = root / "assets/evaluation/reference_schema/files"
    outside.mkdir(parents=True)
    (outside.parent / "README.md").touch()
    (outside / "TrainRun.py").touch()
    (root / "experiment/unknown_dataset").mkdir(parents=True)
    report = check(root, capsys, 1)
    assert {item["path"]: item["rule"] for item in report["violations"]} == {
        "assets/history_experiment/archived_results/README.md": "asset_description",
        "assets/evaluation/reference_schema/files/TrainRun.py": "assets",
        "experiment/unknown_dataset": "experiment",
    }


def test_real_template_reports_only_legacy_names(capsys, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    report = check(TEMPLATE, capsys, 1)
    assert report["checked"] > 70
    assert {item["rule"] for item in report["violations"]} == {"project_name", "name_english_word"}


def test_layout_rejects_and_recovers_at_each_level(capsys, tmp_path):
    root = tmp_path / "BirdClassification"
    shutil.copytree(TEMPLATE, root, ignore=shutil.ignore_patterns(".*", "__pycache__"))
    bundle = root / "assets/evaluation/reference_schema"
    (bundle / "files").mkdir(parents=True)
    (bundle / "scripts").mkdir()
    (bundle / "README.md").write_text("Reference fields for inspecting evaluation reports.")
    (bundle / "files/fields.json").write_text('["accuracy", "sample_count"]')
    (bundle / "scripts/show_fields.py").write_text(
        "from pathlib import Path\nprint(Path(__file__).parents[1].joinpath('files/fields.json').read_text())\n"
    )
    baseline = check(root, capsys, 1)["violations"]
    assert all(item["rule"] == "name_english_word" for item in baseline)

    directories = {
        "data": "root_directory",
        "scratch_runs": "root_directory",
        "src": "root_directory",
        "conf/tasks/unregistered": "configuration_owner",
        "conf/tasks/classification/extra": "conf",
        "experiment/unknown_dataset": "experiment",
        "experiment/cub200/resnet18_mlp/classification/run_01": "experiment",
    }
    files = {
        "orphan.py": "root_file",
        "doc/summary_notes.md": "doc",
        "assets/evaluation/flat.json": "assets",
        "assets/evaluation/reference_schema/files/show_fields.py": "assets",
        "tasks/classification/debug/result.json": "tasks",
        "conf/tasks/classification/main.yaml": "configuration_branch",
        "conf/tasks/classification/extra.yaml": "configuration_branch",
    }
    for relative in directories:
        (root / relative).mkdir(parents=True)
    for relative in files:
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text("{}\n")
    report = check(root, capsys, 1)
    assert {entry["path"]: entry["rule"] for entry in report["violations"] if entry not in baseline} == {
        **directories, **files,
    }
    assert all(entry["expected"] for entry in report["violations"])

    for relative in files:
        (root / relative).unlink()
    for relative in directories:
        (root / relative).rmdir()
    assert check(root, capsys, 1)["violations"] == baseline


def test_layout_uses_base_for_declared_packages(capsys, tmp_path):
    root = tmp_path / "NotesTool"
    package = root / "base/notes_tool"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "notes-tool"\n[tool.setuptools]\npackages = ["notes_tool"]\n'
    )
    check(root, capsys, 0)

    for relative in ("src/notes_tool", "notes_tool"):
        legacy_package = root / relative
        legacy_package.mkdir(parents=True)
        (legacy_package / "__init__.py").write_text("")
    assert {v["path"] for v in check(root, capsys, 1)["violations"]} == {"src", "notes_tool"}


def test_layout_enforces_project_and_child_names(capsys, tmp_path):
    root = tmp_path / "CS769"
    for relative in ("tasks/ranking/ordering", "datasets/sample200", "models/classifier2"):
        (root / relative).mkdir(parents=True)
    assert {v["rule"] for v in check(root, capsys, 1)["violations"]} == {"project_name"}
    for name in ("Context", "ContextMemoryOutputReport", "NLPGraph", "contextMemory"):
        root = root.rename(root.with_name(name))
        assert {v["rule"] for v in check(root, capsys, 1)["violations"]} == {"project_name"}

    root = root.rename(root.with_name("ContextMemory"))
    check(root, capsys, 0)

    named_root = root.with_name("ContextMemoryProject")
    root.rename(named_root)
    check(named_root, capsys, 0)
    invalid = {"tasks/ranking/ordering2": "name_digits", "tasks/ranking/nlp": "name_english_word",
               "tasks/ranking/ordering/merge2.py": "name_digits",
               "tests/test_nlp.py": "name_english_word"}
    (named_root / "tasks/ranking/ordering2").mkdir()
    (named_root / "tasks/ranking/nlp").mkdir()
    (named_root / "tasks/ranking/ordering/merge2.py").touch()
    (named_root / "tests").mkdir()
    (named_root / "tests/test_nlp.py").touch()
    assert {v["path"]: v["rule"] for v in check(named_root, capsys, 1)["violations"]} == invalid
