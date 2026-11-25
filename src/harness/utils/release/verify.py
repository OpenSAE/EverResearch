"""Verify packaged ResearchHarness in a temporary environment.

Run with a release directory and a supported Python. Requires uv and network
access to resolve dependencies unless they are already cached.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile


def check_release(release, work):
    files = set()
    for line in (release / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        if Path(name).name != name or sha256((release / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Invalid release checksum for {name}")
        files.add(name)
    wheel, = (release / name for name in files if name.endswith(".whl"))
    example, = (release / name for name in files if name.endswith("-example.zip"))
    with ZipFile(example) as archive:
        archive.extractall(work)
    project = work / "BirdStudy"
    venv = work / "venv"
    environment = {**os.environ, "RH_STATE_DIR": str(work / "state")}
    scripts = venv / ("Scripts" if os.name == "nt" else "bin")
    python = scripts / ("python.exe" if os.name == "nt" else "python")
    rh = scripts / ("rh.exe" if os.name == "nt" else "rh")
    environment["PATH"] = str(scripts) + os.pathsep + environment.get("PATH", "")

    def run(command, *arguments):
        return subprocess.run(
            [str(command), *map(str, arguments)], cwd=work, env=environment,
            check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout

    run("uv", "venv", "--python", sys.executable, venv)
    run("uv", "pip", "install", "--python", python, wheel)
    health = json.loads(run(rh, "doctor", "--json", "--project", project))
    if health["mode"] != "installed":
        raise ValueError("The release is using a source checkout")
    run(rh, "projects", "project", "check", project)
    run(rh, "projects", "register", "bird-study", "--path", project)
    marker = project / ".researchharness/mode.toml"
    marker.write_text(marker.read_text(encoding="utf-8").replace(
        "enabled = false", "enabled = true"), encoding="utf-8")
    run(rh, "projects", "setup-maintenance", project, "--online")
    run(python, "-IS", project / ".researchharness/maintain.py", "check")
    targets = ["--project", project, "--agent", "codex", "--agent", "claude-code"]
    install = json.loads(run(rh, "skills", "install", *targets))
    repeat = json.loads(run(rh, "skills", "install", *targets))
    if not install or len(repeat) != len(install) or any(r["action"] != "unchanged" for r in repeat):
        raise ValueError("Skill installation failed its repeatability check")
    own = project / ".agents/skills/local-example"
    own.mkdir()
    (own / "SKILL.md").write_text("Project-owned skill.\n", encoding="utf-8")
    run(rh, "skills", "uninstall", *targets)
    if not (own / "SKILL.md").is_file():
        raise ValueError("Uninstall removed a project-owned skill")
    run(rh, "projects", "project", "check", project)
    return {"checksums": len(files), "skills": len(install), "python": health["python"],
            "system": health["system"], "passed": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=Path)
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="researchharness-smoke-") as temporary:
            print(json.dumps(check_release(args.release.resolve(), Path(temporary)), indent=2))
    except subprocess.CalledProcessError as error:
        print(error.stdout, file=sys.stderr, end="")
        print(error.stderr, file=sys.stderr, end="")
        raise SystemExit(error.returncode)
