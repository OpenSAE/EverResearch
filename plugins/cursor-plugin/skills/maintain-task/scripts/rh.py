"""Run the EverResearch CLI bundled with a plugin.

Use from a skill that requires an EverResearch command in the host's
execution environment. The runner installs into a private per-user cache.
"""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv


def bundled_wheel():
    scripts = Path(__file__).resolve().parent
    siblings = scripts.parent.parent
    for directory in (scripts, siblings / "maintain-project" / "scripts"):
        wheels = sorted(directory.glob("ever_research-*.whl"))
        if len(wheels) == 1:
            return wheels[0]
    raise RuntimeError("The OpenSAE runtime is missing from this plugin. Use the complete plugin package.")


def cache_directory():
    if override := os.environ.get("RH_PLUGIN_CACHE_DIR"):
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return (base / "researchharness" / "plugin-runtime").resolve()


def executables(directory):
    scripts = directory / ("Scripts" if os.name == "nt" else "bin")
    suffix = ".exe" if os.name == "nt" else ""
    return scripts / ("python" + suffix), scripts / ("rh" + suffix)


def cli_environment(wheel):
    key = hashlib.sha256(wheel.read_bytes()).hexdigest()
    cache = cache_directory() / sys.implementation.cache_tag / key
    cache.mkdir(parents=True, exist_ok=True)
    current = cache / "current"
    if current.is_file():
        name = current.read_text(encoding="ascii").strip()
        if name.startswith("env-") and Path(name).name == name:
            _, rh = executables(cache / name)
            if rh.is_file():
                return rh

    directory = Path(tempfile.mkdtemp(prefix="env-", dir=cache))
    pointer = cache / (directory.name + ".ready")
    try:
        python, rh = executables(directory)
        if uv := shutil.which("uv"):
            subprocess.run([uv, "venv", "--python", sys.executable, str(directory)],
                           check=True, stdout=sys.stderr)
            subprocess.run([uv, "pip", "install", "--python", str(python), str(wheel)],
                           check=True, stdout=sys.stderr)
        else:
            venv.EnvBuilder(with_pip=True).create(directory)
            subprocess.run([str(python), "-I", "-m", "pip", "--disable-pip-version-check",
                            "install", str(wheel)], check=True, stdout=sys.stderr)
        if not rh.is_file():
            raise RuntimeError("The bundled OpenSAE package did not provide the rh command.")
        pointer.write_text(directory.name + "\n", encoding="ascii")
        pointer.replace(current)
        return rh
    except BaseException:
        pointer.unlink(missing_ok=True)
        shutil.rmtree(directory, ignore_errors=True)
        raise


def main():
    try:
        if sys.version_info < (3, 11) or sys.version_info >= (3, 14):
            raise RuntimeError("EverResearch requires Python 3.11, 3.12, or 3.13.")
        wheel = bundled_wheel()
        rh = cli_environment(wheel)
        environment = os.environ.copy()
        environment["PATH"] = str(rh.parent) + os.pathsep + environment.get("PATH", "")
        environment["RH_PLUGIN_CLI"] = str(rh)
        environment["RH_PLUGIN_WHEEL"] = str(wheel)
        return subprocess.run([str(rh), *sys.argv[1:]], env=environment).returncode
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"EverResearch runtime unavailable: {error}", file=sys.stderr)
        return 78


if __name__ == "__main__":
    raise SystemExit(main())
