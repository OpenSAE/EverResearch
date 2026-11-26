"""Report maintenance status or run a structural check in the selected mode.

Run this launcher from a project configured for online or offline maintenance.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib


DIRECTORY = Path(__file__).absolute().parent
PROJECT = DIRECTORY.parent
OFFLINE = DIRECTORY / "offline"
ONLINE = DIRECTORY / "online"


def require_file(path):
    if path.parent.is_symlink() or path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular project maintenance file: {path}")
    return path


def enabled():
    mode = tomllib.loads(require_file(DIRECTORY / "mode.toml").read_text(encoding="utf-8"))
    if set(mode) != {"enabled"} or type(mode["enabled"]) is not bool:
        raise ValueError("Set enabled = true or enabled = false in .researchharness/mode.toml.")
    return mode["enabled"]


def offline(action):
    guide = require_file(OFFLINE / "operations.md")
    checker = require_file(OFFLINE / "check.py")
    if action == "status":
        print(f"offline\n{guide}")
        return 0
    return subprocess.run([sys.executable, "-IS", str(checker)], cwd=PROJECT).returncode


def online_guide(project, binding, root):
    """Verify that the central record and guide belong to this project."""
    if (Path(binding["path"]) != project or not binding["settings"]["skills"]
            or not binding["skills"] or binding["skill_entry"] != "central-guide"
            or not binding["maintenance_guide"]):
        raise ValueError("The central registration, shared skills, or online guide is unavailable for this project.")
    guide = Path(binding["maintenance_guide"])
    if not guide.resolve().is_relative_to(root):
        raise ValueError("The online guide must be inside the EverResearch workspace.")
    return require_file(guide)


def online(action):
    connection = json.loads(require_file(ONLINE / "connection.json").read_text(encoding="utf-8"))
    root = (PROJECT / connection["root"]).resolve(strict=True)
    environment = os.environ.copy()
    if connection.get("installed") is True:
        executable = connection.get("plugin_cli") or connection.get("cli")
        if executable and (not Path(executable).is_file() or not os.access(executable, os.X_OK)):
            raise ValueError(f"EverResearch CLI moved or is unavailable: {executable}. Reapply the online connection using the intended installation.")
        if not executable:
            executable = shutil.which("rh")
        if executable is None:
            raise ValueError("Open the EverResearch plugin or install the ever-research package from OpenSAE.")
        command = [executable, "projects"]
        environment["RH_STATE_DIR"] = str(root)
    else:
        require_file(root / "src/harness/cli.py")
        require_file(root / "src/harness/projects/operations.md")
        launcher = (
            "import sys; from pathlib import Path; root = Path(sys.argv.pop(1)); "
            "sys.path.insert(0, str(root / 'src')); from harness.cli import main; "
            "raise SystemExit(main(sys.argv[1:]))"
        )
        interpreter = connection.get("python", sys.executable)
        if not Path(interpreter).is_file():
            raise ValueError(f"EverResearch Python moved or is unavailable: {interpreter}. Reapply the online connection using the intended environment.")
        command = [interpreter, "-I", "-c", launcher, str(root), "projects", "--harness-root", str(root)]
    state = subprocess.run(
        [*command, "status", connection["project_id"]],
        cwd=PROJECT, env=environment, check=True, stdout=subprocess.PIPE, text=True, encoding="utf-8",
    )
    guide = online_guide(PROJECT, json.loads(state.stdout), root)
    if action == "status":
        print(f"online\n{guide}")
        return 0
    return subprocess.run([*command, "project", "check", str(PROJECT), "--json"], cwd=PROJECT, env=environment).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "check"])
    args = parser.parse_args()
    mode = "Failed to read from switch"
    try:
        if enabled():
            mode = "Online maintenance is unavailable"
            return online(args.action)
        mode = "Offline maintenance not available"
        return offline(args.action)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"{mode}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
