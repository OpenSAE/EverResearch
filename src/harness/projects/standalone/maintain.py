"""Select the maintenance source by the project switch and run the structural check of the source.

Run from project status or check.Only offline checks within items are run when switches are closed;
Using a mounted central program on startup, which failed to return when not available.
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
        raise ValueError(f"The missing project maintenance file or file is not a local normal file:{path}")
    return path


def enabled():
    mode = tomllib.loads(require_file(DIRECTORY / "mode.toml").read_text(encoding="utf-8"))
    if set(mode) != {"enabled"} or type(mode["enabled"]) is not bool:
        raise ValueError("mode.toml Need to be specified enabled = true or false")
    return mode["enabled"]


def offline(action):
    guide = require_file(OFFLINE / "operations.md")
    checker = require_file(OFFLINE / "check.py")
    if action == "status":
        print(f"offline\n{guide}")
        return 0
    return subprocess.run([sys.executable, "-IS", str(checker)], cwd=PROJECT).returncode


def online(action):
    connection = json.loads(require_file(ONLINE / "connection.json").read_text(encoding="utf-8"))
    root = (PROJECT / connection["root"]).resolve(strict=True)
    environment = os.environ.copy()
    if connection.get("installed") is True:
        executable = shutil.which("rh")
        if executable is None and connection.get("plugin_cli"):
            candidate = Path(connection["plugin_cli"])
            if candidate.is_file():
                executable = str(candidate)
        if executable is None:
            raise ValueError("Open the ResearchHarness plugin in this environment or install the OpenSAE CLI")
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
        command = [sys.executable, "-I", "-c", launcher, str(root), "projects", "--harness-root", str(root)]
    state = subprocess.run(
        [*command, "status", connection["project_id"]],
        cwd=PROJECT, env=environment, check=True, stdout=subprocess.PIPE, text=True, encoding="utf-8",
    )
    binding = json.loads(state.stdout)
    if (Path(binding["path"]) != PROJECT or not binding["settings"]["skills"]
            or not binding["skills"] or binding["skill_entry"] != "central-guide"
            or not binding["maintenance_guide"]):
        raise ValueError("Central registration, original skills or online instructions are not available, please remount the item")
    guide = Path(binding["maintenance_guide"])
    if not guide.resolve().is_relative_to(root):
        raise ValueError("Online notes must be located ResearchHarness Into the warehouse.")
    require_file(guide)
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
        print(f"{mode}:{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
