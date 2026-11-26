"""Report maintenance status or run a structural check in the selected mode.

Run this launcher from a project configured for online or offline maintenance.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


DIRECTORY = Path(__file__).absolute().parent
PROJECT = DIRECTORY.parent
OFFLINE = DIRECTORY / "offline"
ONLINE = DIRECTORY / "online"
BOUND_RUNTIME = "RH_BOUND_PROJECT_RUNTIME"


def require_file(path):
    if path.parent.is_symlink() or path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular project maintenance file: {path}")
    return path


def enabled():
    text = require_file(DIRECTORY / "mode.toml").read_text(encoding="utf-8")
    if tomllib is None:
        contents = "\n".join(line.partition("#")[0] for line in text.splitlines())
        match = re.fullmatch(r'\s*(?:enabled|"enabled"|\'enabled\')\s*=\s*(true|false)\s*', contents)
        mode = {"enabled": match[1] == "true"} if match else {}
    else:
        mode = tomllib.loads(text)
    if set(mode) != {"enabled"} or type(mode["enabled"]) is not bool:
        raise ValueError(f"Set enabled = true or enabled = false in {DIRECTORY / 'mode.toml'}.")
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
    try:
        guide.resolve().relative_to(root)
    except ValueError:
        raise ValueError("The online guide must be inside the EverResearch workspace.")
    return require_file(guide)


def online_command(connection, project):
    """Resolve the project’s selected runtime independently of the caller's Python."""
    root = (project / connection["root"]).resolve(strict=True)
    environment = os.environ.copy()
    environment[BOUND_RUNTIME] = str(project)
    interpreter = connection.get("python")
    if interpreter and (not Path(interpreter).is_file() or not os.access(interpreter, os.X_OK)):
        raise ValueError(f"EverResearch Python is unavailable at {interpreter}. Run setup-maintenance with the intended installation.")
    if connection.get("installed") is True and interpreter:
        command = [interpreter, "-I", "-m", "harness.cli", "projects"]
        environment["RH_STATE_DIR"] = str(root)
    elif connection.get("installed") is True:
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
        command = [interpreter or sys.executable, "-I", "-c", launcher, str(root), "projects", "--harness-root", str(root)]
    return command, environment, root


def online(action):
    connection = json.loads(require_file(ONLINE / "connection.json").read_text(encoding="utf-8"))
    command, environment, root = online_command(connection, PROJECT)
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
