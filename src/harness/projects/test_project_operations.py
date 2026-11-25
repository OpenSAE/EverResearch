"""Protect the full-fledged in-house operation of shared skills, resource start-up and structural results.

Validate the official command interface using the newly created project directory, interpreter environment and example page.
"""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile

import pytest

from harness.cli import main


SEARCH_PARAGRAPH = 'Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.'


@pytest.fixture
def workspace(tmp_path):
    root = tmp_path / "central"
    project = tmp_path / "project"
    skill = root / ".agents/skills/example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Example\n")
    project.mkdir()
    return root, project, skill


@pytest.fixture
def command(workspace, capsys):
    root, project, _ = workspace

    def invoke(*args, expected=0):
        assert main(["projects", "--harness-root", str(root), *args]) == expected
        capture = capsys.readouterr()
        return json.loads(capture.out) if capture.out and expected == 0 else capture.err

    invoke("register", "example", "--path", str(project))
    return invoke


def test_shared_skills_preserve_project_content(command, workspace):
    root, project, central_skill = workspace
    own = project / ".agents/skills/local"
    own.mkdir(parents=True)
    (own / "SKILL.md").write_text("# Project-owned skill\n")
    legacy_link = own.parent / "example"
    legacy_link.symlink_to(central_skill, target_is_directory=True)
    legacy_guide = own.parent / "researchharness/SKILL.md"
    legacy_guide.parent.mkdir()
    legacy_guide.write_bytes(Path(__file__).with_name("researchharness.skill.md.in").read_bytes())
    agents = project / "AGENTS.md"
    agents.write_text("# Project instructions\n")
    client = project / ".codex/config.toml"
    client.parent.mkdir()
    client.write_text("# Existing client settings\n")
    linked = command("apply", "example")
    assert linked["skills"] == {"example": True}
    assert command("project", "status", str(project))["mode"] == "legacy"
    assert command("project", "status", str(project))["state"] == "managed"
    assert Path(linked["shared_skill_directory"]) == central_skill.parent
    assert not legacy_link.is_symlink()
    assert not legacy_guide.exists()
    assert "../central/.agents/skills/example/SKILL.md" in agents.read_text()
    command("apply", "example")
    assert agents.read_text().count("<!-- researchharness:projects -->") == 1
    assert agents.read_text().count(SEARCH_PARAGRAPH) == 1
    assert agents.read_text().startswith("# Project instructions\n")
    disabled = command("set", "example", "--skills", "off")
    assert disabled["skills"] == {}
    assert command("project", "status", str(project))["state"] == "unmanaged"
    assert disabled["maintenance_guide"] is None
    assert disabled["shared_skill_directory"] is None
    assert "../central" not in agents.read_text()
    assert agents.read_text().count(SEARCH_PARAGRAPH) == 1
    assert (root / "src/project/maintained/example/project.yaml").is_file()
    assert (own / "SKILL.md").read_text() == "# Project-owned skill\n"
    assert client.read_text() == "# Existing client settings\n"


def test_legacy_project_records_remain_readable(command, workspace):
    root, _, _ = workspace
    old = root / "src/project/example"
    old.mkdir(parents=True)
    (old / "project.yaml").write_text("project_id: example\nskills: false\n")
    (old / "resources.json").write_text('{"data": {}, "python": null}')
    saved = {"skills": False, "lightweight_checks": False}
    assert command("status", "example")["settings"] == saved
    assert command("resources", "example") == {"data": {}, "python": None}
    current = root / "src/project/maintained/example"
    current.parent.mkdir()
    old.rename(current)
    assert command("status", "example")["settings"] == saved
    assert command("resources", "example") == {"data": {}, "python": None}


@pytest.mark.parametrize("custom_skill_directory", [False, True])
def test_apply_routes_maintenance_and_persists_check_authorization(
    command, workspace, custom_skill_directory,
):
    root, project, _ = workspace
    operations = root / "src/harness/projects/operations.md"
    operations.parent.mkdir(parents=True)
    operations.write_bytes(Path(__file__).with_name("operations.md").read_bytes())
    for name in ("maintain-dataset", "maintain-conf"):
        skill = root / ".agents/skills" / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"# {name}\n")
    if custom_skill_directory:
        owned = project / "skills"
        owned.mkdir()
        (project / ".agents").mkdir()
        (project / ".agents/skills").symlink_to(owned, target_is_directory=True)
    settings = root / "src/project/maintained/example/project.yaml"
    settings.parent.mkdir(parents=True)
    settings.write_text("# Existing settings\nproject_id: example\nskills: true\n")
    agents = project / "AGENTS.md"
    agents.write_text("# Existing project instructions\n")

    assert command("apply", "example")["settings"]["lightweight_checks"] is False
    text = agents.read_text()
    assert "../central/.agents/skills/maintain-dataset/SKILL.md" in text
    assert "../central/.agents/skills/maintain-conf/SKILL.md" in text
    assert not (project / ".agents/researchharness-skills").exists()
    assert "maintain-model" not in text
    assert "Lightweight follow-up checks follow the task authorization" in text
    assert "Choose the operation before making changes" in text
    assert "When asked to implement a feature" in text
    assert "If an existing parameter supports the request" in text
    assert "add per-class accuracy to an existing classification task" in text
    assert "keep the existing top-level directories" in text
    assert "Before running a command, confirm its working directory, output paths, and cache location" in text
    assert "Review the paths after each batch" in text
    sections = re.findall(r'\]\(<([^>]+/operations\.md)#([a-z-]+)>\)', text)
    assert len(sections) == 14
    for path, anchor in sections:
        assert (project / path).resolve() == operations
        assert f'<a id="{anchor}"></a>' in operations.read_text()

    applied = command("apply", "example", "--lightweight-checks", "on")
    assert applied["settings"] == applied["last_applied_settings"] == {
        "skills": True, "lightweight_checks": True,
    }
    assert "Lightweight follow-up checks are enabled" in agents.read_text()
    assert "rh projects layout check" in agents.read_text()
    assert "Run one structure check for each state of the project tree" in agents.read_text()
    assert settings.read_text().startswith("# Existing settings\n")
    assert "lightweight_checks: true" in settings.read_text()
    assert command("apply", "example")["last_applied_settings"]["lightweight_checks"] is True
    command("set", "example", "--skills", "off")
    assert "Daily maintenance and lightweight checks" not in agents.read_text()
    command("set", "example", "--skills", "on")
    assert "Lightweight follow-up checks are enabled" in agents.read_text()
    command("apply", "example", "--lightweight-checks", "off")
    assert "Lightweight follow-up checks follow the task authorization" in agents.read_text()
    assert agents.read_text().startswith("# Existing project instructions\n")
    assert agents.read_text().count("<!-- researchharness:projects -->") == 1


def test_project_mode_reads_central_originals_only_online(command, workspace):
    root, project, central_skill = workspace
    shutil.copytree(
        Path(__file__).parents[1], root / "src/harness",
        ignore=shutil.ignore_patterns("templates", "__pycache__"),
    )
    command("setup-maintenance", str(project), "--online")
    instructions = (project / "AGENTS.md").read_text()
    assert instructions.count(SEARCH_PARAGRAPH) == 1
    assert instructions.index(SEARCH_PARAGRAPH) < instructions.index("## Choose the maintenance mode")
    command("apply", "example")
    assert (project / "AGENTS.md").read_text() == instructions
    launcher = project / ".researchharness/maintain.py"
    mode = launcher.parent / "mode.toml"
    connection = launcher.parent / "online/connection.json"

    def status():
        return subprocess.run(
            [sys.executable, "-IS", str(launcher), "status"], cwd=project,
            text=True, capture_output=True,
        )

    result = status()
    assert result.returncode == 0, result.stderr
    selected, guide_path = result.stdout.splitlines()
    assert command("project", "status", str(project)) == {
        "path": str(project), "state": "managed", "mode": "online", "guide": guide_path,
    }
    guide = Path(guide_path)
    assert selected == "online"
    assert guide.is_relative_to(root)
    skill_path = re.search(r"\]\(([^)]+/example/SKILL\.md)\)", guide.read_text())[1]
    assert (guide.parent / skill_path).resolve() == central_skill / "SKILL.md"
    assert list(connection.parent.iterdir()) == [connection]
    assert not (project / ".agents").exists()

    original = mode.read_text()
    original_connection = connection.read_text()
    mode.write_text("enabled = false\n")
    connection.write_text("unreadable connection")
    result = status()
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "offline", str(launcher.parent / "offline/operations.md"),
    ]
    assert command("status", "example")["shared_skill_directory"] is None
    assert not list(project.rglob("SKILL.md"))
    (project / "data").mkdir()
    report = subprocess.run(
        [sys.executable, "-IS", str(launcher), "check"], cwd=project,
        text=True, capture_output=True,
    )
    assert report.returncode == 1, report.stderr
    assert {"path": "data", "rule": "root_directory"} in json.loads(report.stdout)["violations"]

    mode.write_text(original)
    assert command("project", "status", str(project))["state"] == "unavailable"
    result = status()
    assert result.returncode == 2
    assert "Online maintenance is unavailable" in result.stderr
    assert not result.stdout

    connection.write_text(original_connection)
    result = status()
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["online", str(guide)]
    assert (project / "AGENTS.md").read_text() == instructions


def test_standalone_setup_preserves_project_instructions(command, workspace):
    from harness.projects.setup_backup import LARGE_FILE_BYTES

    _, project, central_skill = workspace
    agents = project / "AGENTS.md"
    original = "# Project instructions\n\nLocal working rules.\n"
    agents.write_text(original)
    assert command("project", "status", str(project)) == {
        "path": str(project), "state": "unmanaged", "mode": None, "guide": None,
    }
    assert list(project.iterdir()) == [agents]
    ignore = project / ".gitignore"
    ignore.write_text("# Existing ignore rules\n")
    legacy = project / ".agents/skills/example"
    legacy.parent.mkdir(parents=True)
    legacy.symlink_to(central_skill, target_is_directory=True)
    project_files = {
        "train.py": b"print('train')\n",
        "eval.py": b"print('eval')\n",
        "configs/default.yaml": b"batch_size: 4\n",
        "src/model.py": b"class Probe: pass\n",
        "utils/data.py": b"def load(): return []\n",
        "doc/README.md": b"# Local research notes\n",
        ".editorconfig": b"root = true\n",
    }
    skipped = (
        ".git/config", ".scratch/private.py", "venv/train.py", "node_modules/example.js",
        "__pycache__/model.pyc", "runtime/python_env/pyvenv.cfg", "runtime/python_env/train.py",
    )
    for name, content in {**project_files, **dict.fromkeys(skipped, b"skip")}.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    data = project / "data"
    data.mkdir()
    for name in ("small.npy", "photo.JPG", "weights.pt", "samples.zip", "audio.wav", "video.mp4"):
        (data / name).write_bytes(b"data")
    large = project / "artifact.blob"
    with large.open("wb") as stream:
        stream.truncate(LARGE_FILE_BYTES + 1)
    setup = command("setup-maintenance", str(project))
    assert setup["mode"] == "offline"
    archive = project / ".researchharness/backups/initial-setup.tar.gz"
    assert Path(setup["backup"]) == archive
    original_backup = archive.read_bytes()
    with tarfile.open(archive) as bundle:
        assert bundle.extractfile("files/AGENTS.md").read().decode() == original
        assert bundle.extractfile("files/.gitignore").read() == b"# Existing ignore rules\n"
        manifest = json.load(bundle.extractfile("manifest.json"))
        assert set(manifest["files"]) == {*project_files, "AGENTS.md", ".gitignore"}
        for name, content in project_files.items():
            assert bundle.extractfile(f"files/{name}").read() == content
        assert {item["path"]: item["size_bytes"] for item in manifest["large_files"]} == {
            large.name: LARGE_FILE_BYTES + 1,
            **{f"data/{item.name}": 4 for item in data.iterdir()},
        }
        assert f"files/{large.name}" not in bundle.getnames()
        assert manifest["links"] == {".agents/skills/example": str(central_skill)}
        assert ".researchharness/mode.toml" in manifest["created_paths"]
    assert "/.researchharness/backups/" in ignore.read_text().splitlines()
    assert not legacy.is_symlink()
    generated = agents.read_text()
    launcher = project / ".researchharness/maintain.py"
    launcher.write_text("raise AssertionError('status must not run project code')\n")
    report = command("project", "status", str(project))
    assert report["state"] == "managed"
    assert report["mode"] == "offline"
    assert report["guide"] == str(launcher.parent / "offline/operations.md")
    assert generated.startswith(original)
    assert generated.count(SEARCH_PARAGRAPH) == 1
    (archive.parent / "initial-setup.tar.lock").touch()
    assert command("setup-maintenance", str(project))["backup"] is None
    assert list(archive.parent.iterdir()) == [archive]
    assert archive.read_bytes() == original_backup
    assert agents.read_text() == generated
    (launcher.parent / "offline/operations.md").unlink()
    assert command("project", "status", str(project))["state"] == "unavailable"


def test_retried_setup_keeps_the_original_backup(command, workspace, monkeypatch):
    from harness.projects import manage

    _, project, _ = workspace
    agents = project / "AGENTS.md"
    agents.write_bytes(b"# Original\n")
    save_bytes = manage.save_bytes

    def interrupt(path, *args, **kwargs):
        if path == agents:
            raise OSError("Interrupted setup")
        return save_bytes(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(manage, "save_bytes", interrupt)
        assert "Interrupted setup" in command("setup-maintenance", str(project), expected=1)
    archive = project / ".researchharness/backups/initial-setup.tar.gz"
    before_retry = archive.read_bytes()
    assert not (project / ".researchharness/mode.toml").exists()
    agents.write_bytes(b"# Edited before retry\n")
    assert Path(command("setup-maintenance", str(project))["backup"]) == archive
    assert archive.read_bytes() == before_retry
    assert agents.read_bytes().startswith(b"# Edited before retry\n")


def test_initial_backup_prioritizes_project_source_under_the_total_limit(command, workspace, monkeypatch):
    from harness.projects import setup_backup

    _, project, _ = workspace
    monkeypatch.setattr(setup_backup, "BACKUP_BUDGET_BYTES", 18)
    (project / "first.misc").write_bytes(b"a" * 15)
    (project / "model.py").write_bytes(b"pass   \n")
    (project / "config.yml").write_bytes(b"value: 1")
    (project / "report.md").write_bytes(b"report")
    result = command("setup-maintenance", str(project))
    archive = Path(result["backup"])
    with tarfile.open(archive) as bundle:
        manifest = json.load(bundle.extractfile("manifest.json"))
        assert manifest["files"] == ["config.yml", "model.py"]
        assert sum(item.size for item in bundle if item.name.startswith("files/")) == 16
        assert manifest["large_files"] == [
            {"path": "report.md", "size_bytes": 6}, {"path": "first.misc", "size_bytes": 15},
        ]


def test_run_uses_bound_python_data_and_project(command, workspace, tmp_path):
    _, project, _ = workspace
    data = tmp_path / "data" / "dataset with spaces"
    data.mkdir(parents=True)
    python = tmp_path / "env/bin/python"
    python.parent.mkdir(parents=True)
    python.symlink_to(sys.executable)
    (python.parent.parent / "pyvenv.cfg").write_text(
        f"home = {Path(sys.executable).resolve().parent}\ninclude-system-site-packages = false\n"
    )
    script = project / "check.py"
    result = project / "observed.json"
    script.write_text(
        "import json, os, pathlib, sys\n"
        "pathlib.Path('observed.json').write_text(json.dumps({"
        "'cwd': os.getcwd(), 'data': sys.argv[1], 'env': os.environ['PROJECT_DATA'],"
        " 'python': sys.executable, 'prefix': sys.prefix}))\n"
    )
    assert "workspace data root" in command("bind", "example", "--data", f"main={project}", expected=1)
    command("bind", "example", "--python", str(python), "--data", f"main={data}")
    assert command("list") == [
        {"project": "example", "path": str(project), "data": {"main": str(data)}, "python": str(python)}
    ]
    command("run", "--env", "PROJECT_DATA={data:main}", "example", "--",
            "check.py", "{data:main}")
    assert json.loads(result.read_text()) == {
        "cwd": str(project), "data": str(data), "env": str(data), "python": str(python),
        "prefix": str(python.parent.parent),
    }
    assert "missing" in command("run", "example", "--", "check.py", "{data:missing}", expected=1)
    command("bind", "example", "--clear-python", "--remove-data", "main")
    assert command("resources", "example") == {"data": {}, "python": None}


def test_review_pins_export_and_keeps_other_versions_selectable(command, tmp_path):
    html = tmp_path / "index.html"
    first = b"<!doctype html><title>First export</title>"
    html.write_bytes(first)
    add = ("structure", "add", "example", str(html))
    a = command(*add, "--revision", "commit-a", "--scope", "project root")
    assert Path(a["page"]).parts[-7:-3] == ("src", "project", "maintained", "example")
    html.write_text("<!doctype html><title>Second export</title>")
    b = command(*add, "--revision", "commit-b", "--scope", "src")
    assert Path(a["page"]).read_bytes() == first
    assert b["review"] is None
    result = command("structure", "review", "example", a["id"], "--decision", "approved")
    assert result["review"]["sha256"] == a["sha256"]
    assert [item["id"] for item in command("structure", "list", "example")] == [b["id"], a["id"]]
    Path(a["page"]).write_text("changed")
    assert "inconsistent" in command("structure", "show", "example", a["id"], expected=1)
