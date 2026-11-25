"""Verify packaged ResearchHarness in a temporary environment.

Run with a release directory and a supported Python. Requires uv and network
access to resolve dependencies unless they are already cached.
"""

import argparse
from hashlib import sha256
from io import BytesIO
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from unittest.mock import patch
from zipfile import ZipFile


PLUGIN_ENTRIES = {
    "agent-plugin": "plugin.json",
    "codex-plugin": ".codex-plugin/plugin.json",
    "cursor-plugin": ".cursor-plugin/plugin.json",
    "claude-plugin": ".claude-plugin/plugin.json",
    "gemini-extension": "gemini-extension.json",
    "opencode-plugin": "package.json",
    "openclaw-plugin": "openclaw.plugin.json",
}


def verify_plugins(release, wheel, work):
    """Check every plugin's skill inventory and run the bundled CLI."""
    version = wheel.name.split("-")[1]
    wheel_data = wheel.read_bytes()
    with ZipFile(wheel) as installed:
        metadata_name, = (n for n in installed.namelist() if n.endswith(".dist-info/METADATA"))
        if b"Name: ever-research\n" not in installed.read(metadata_name):
            raise ValueError("Incorrect Python package name")
        with ZipFile(BytesIO(installed.read("harness/public_resources.zip"))) as resources:
            expected = {
                name.removeprefix(".agents/"): resources.read(name)
                for name in resources.namelist() if name.startswith(".agents/skills/")
            }

    runtime_lock = {"filename": wheel.name, "sha256": sha256(wheel_data).hexdigest(),
                    "size": len(wheel_data)}

    rendered_skills = {}

    def compare(actual, label, *, bundled=True):
        for name, body in expected.items():
            runner = name.removesuffix("/SKILL.md") + "/scripts/rh.py"
            if name.endswith("/SKILL.md") and runner in actual:
                _, frontmatter, _ = body.split(b"---", 2)
                if actual[name].split(b"---", 2)[1] != frontmatter:
                    raise ValueError(f"Unexpected skill metadata in {label}: {name}")
                if rendered_skills.setdefault(name, actual[name]) != actual[name]:
                    raise ValueError(f"Different skill instructions in {label}: {name}")
            elif actual.get(name) != body:
                raise ValueError(f"Unexpected skill file in {label}: {name}")
        for name in actual.keys() - expected.keys():
            if name.endswith(".whl") and bundled and actual[name] == wheel_data:
                continue
            if name.endswith("/scripts/rh-runtime.json") and json.loads(actual[name]) == runtime_lock:
                continue
            if not name.endswith("/scripts/rh.py"):
                raise ValueError(f"Unexpected plugin addition in {label}: {name}")
            if name.removesuffix("/rh.py") + "/rh-runtime.json" not in actual:
                raise ValueError(f"Missing runtime metadata in {label}: {name}")
        if bundled and actual.get(f"skills/maintain-project/scripts/{wheel.name}") != wheel_data:
            raise ValueError(f"Missing bundled runtime in {label}")

    readmes = set()
    for platform, manifest in PLUGIN_ENTRIES.items():
        with ZipFile(release / f"ever-research-{version}-{platform}.zip") as archive:
            actual = {name: archive.read(name) for name in archive.namelist()
                      if name.startswith("skills/")}
            if manifest not in archive.namelist():
                raise ValueError(f"Missing manifest in {platform}")
            readme = archive.read("README.md")
            if b"@DOWNLOAD@" in readme or b"## Install" not in readme:
                raise ValueError(f"Incomplete installation guide in {platform}")
            readmes.add(readme)
            compare(actual, platform)
            if platform in {"claude-plugin", "agent-plugin"}:
                destination = work / platform
                if platform == "claude-plugin":
                    files = [n for n in actual if n.startswith("skills/maintain-project/")]
                    archive.extractall(destination, files)
                else:
                    archive.extractall(destination)
    if len(readmes) != len(PLUGIN_ENTRIES):
        raise ValueError("Each plugin format must have its own README")
    with tarfile.open(release / f"opensae-ever-research-dsh-{version}.tgz") as archive:
        manifest = json.load(archive.extractfile("package/package.json"))
        if "bundle" not in manifest.get("dsh", {}):
            raise ValueError("Missing DeepSeek Harness bundle manifest")
        actual = {entry.name.removeprefix("package/"): archive.extractfile(entry).read()
                  for entry in archive.getmembers()
                  if entry.isfile() and entry.name.startswith("package/skills/")}
        compare(actual, "DeepSeek")
    with ZipFile(release / f"ever-research-{version}-marketplace.zip") as archive:
        platforms = ("agent-plugin", "claude-plugin", "codex-plugin", "cursor-plugin",
                     "gemini-extension", "opencode", "openclaw", "deepseek")
        for platform in platforms:
            prefix = f"plugins/{platform}/"
            files = {name.removeprefix(prefix): archive.read(name) for name in archive.namelist()
                     if name.startswith(prefix + "skills/")}
            compare(files, platform + " marketplace", bundled=False)
        files = [name for name in archive.namelist()
                 if name.startswith("plugins/agent-plugin/skills/maintain-project/scripts/")]
        archive.extractall(work / "marketplace", files)
    verify_runtime_download(work, wheel_data, runtime_lock)
    return len(PLUGIN_ENTRIES) + 1


def verify_runtime_download(work, wheel_data, metadata):
    script = work / "marketplace/plugins/agent-plugin/skills/maintain-project/scripts/rh.py"
    spec = importlib.util.spec_from_file_location("test_plugin_runtime", script)
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    cache = work / "download-cache"
    with patch.object(launcher, "cache_directory", return_value=cache):
        with patch.object(launcher, "urlopen", return_value=BytesIO(b"corrupt")):
            try:
                launcher.runtime_wheel()
            except RuntimeError as error:
                if "checksum" not in str(error):
                    raise
            else:
                raise ValueError("The launcher accepted a corrupted download")
        with patch.object(launcher, "urlopen", return_value=BytesIO(wheel_data)) as download:
            cached = launcher.runtime_wheel()
            version = metadata["filename"].split("-")[1]
            url = (f"https://github.com/OpenSAE/EverResearch/releases/download/v{version}/"
                   f"{metadata['filename']}")
            request = download.call_args.args[0]
            if (cached.read_bytes() != wheel_data or request.full_url != url
                    or request.get_header("Accept") != "application/octet-stream"):
                raise ValueError("The launcher did not cache the pinned Release wheel")
        with patch.object(launcher, "urlopen", side_effect=AssertionError("Unexpected download")):
            if launcher.runtime_wheel() != cached:
                raise ValueError("The launcher did not reuse its verified cache")


def check_release(release, work):
    files = set()
    for line in (release / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        if Path(name).name != name or sha256((release / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Invalid release checksum for {name}")
        files.add(name)
    wheel, = (release / name for name in files if name.endswith(".whl"))
    plugins = verify_plugins(release, wheel, work)
    example, = (release / name for name in files if name.endswith("-example.zip"))
    with ZipFile(example) as archive:
        archive.extractall(work)
    project = work / "BirdStudy"
    environment = {**os.environ, "RH_STATE_DIR": str(work / "state"),
                   "RH_PLUGIN_CACHE_DIR": str(work / "plugin-cache")}
    for platform in ("claude-plugin", "agent-plugin"):
        runner = work / platform / "skills/maintain-project/scripts/rh.py"
        subprocess.run([sys.executable, "-I", str(runner), "projects", "project", "check", str(project), "--json"],
                       cwd=work, env=environment, check=True, capture_output=True, text=True)
    venv = work / "venv"
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
    run(rh, "projects", "project", "check", project, "--json")
    demo = work / "QuickDemo"
    run(rh, "utils", "quick-demo", demo)
    mixed = demo / "MixedStudy"
    if json.loads(run(rh, "projects", "project", "status", mixed))["state"] != "unmanaged":
        raise ValueError("The installed CLI did not recognize the unconfigured project")
    preview = run(rh, "projects", "project", "check", mixed)
    if "Paste into your agent" not in preview:
        raise ValueError("The installed CLI did not show the onboarding report")
    data = mixed / "sample.npy"
    data.write_bytes(b"example dataset")
    setup = json.loads(run(rh, "projects", "setup-maintenance", mixed))
    backup = Path(setup["backup"])
    with tarfile.open(backup) as archive:
        manifest = json.load(archive.extractfile("manifest.json"))
        if ("files/train.py" not in archive.getnames() or "files/sample.npy" in archive.getnames()
                or {"path": data.name, "size_bytes": data.stat().st_size} not in manifest["large_files"]):
            raise ValueError("The installed CLI did not back up source and inventory data as expected")
    if json.loads(run(rh, "projects", "setup-maintenance", mixed))["backup"] is not None:
        raise ValueError("The installed CLI attempted a second initial backup")
    run(rh, "projects", "register", "bird-study", "--path", project)
    marker = project / ".researchharness/mode.toml"
    marker.write_text(marker.read_text(encoding="utf-8").replace(
        "enabled = false", "enabled = true"), encoding="utf-8")
    run(rh, "projects", "setup-maintenance", project, "--online")
    if json.loads(run(rh, "projects", "project", "status", project))["state"] != "managed":
        raise ValueError("The installed CLI did not recognize the configured project")
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
    run(rh, "projects", "project", "check", project, "--json")
    return {"checksums": len(files), "skills": len(install), "plugin_formats": plugins,
            "python": health["python"],
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
