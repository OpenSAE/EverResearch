"""保护共享技能、资源启动和结构成果的完整本机操作。

使用新建的项目目录、解释器环境和示例页面，验证正式命令接口。
"""

import json
from pathlib import Path
import sys

import pytest

from harness.cli import main


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
    _, project, central_skill = workspace
    own = project / ".agents/skills/local"
    own.mkdir(parents=True)
    agents = project / "AGENTS.md"
    agents.write_text("# Project instructions\n")
    client = project / ".codex/config.toml"
    client.parent.mkdir()
    client.write_text("# Existing client settings\n")
    linked = command("apply", "example")
    assert linked["skills"] == {"example": True}
    assert (own.parent / "example").resolve() == central_skill
    command("apply", "example")
    assert agents.read_text().count("<!-- researchharness:projects -->") == 1
    assert agents.read_text().startswith("# Project instructions\n")
    assert command("set", "example", "--skills", "off")["skills"] == {"example": False}
    assert own.is_dir()
    assert client.read_text() == "# Existing client settings\n"


def test_run_uses_bound_python_data_and_project(command, workspace, tmp_path):
    _, project, _ = workspace
    data = tmp_path / "dataset with spaces"
    data.mkdir()
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
    html.write_text("<!doctype html><title>Second export</title>")
    b = command(*add, "--revision", "commit-b", "--scope", "src")
    assert Path(a["page"]).read_bytes() == first
    assert b["review"] is None
    result = command("structure", "review", "example", a["id"], "--decision", "approved")
    assert result["review"]["sha256"] == a["sha256"]
    assert [item["id"] for item in command("structure", "list", "example")] == [b["id"], a["id"]]
    Path(a["page"]).write_text("changed")
    assert "不一致" in command("structure", "show", "example", a["id"], expected=1)
