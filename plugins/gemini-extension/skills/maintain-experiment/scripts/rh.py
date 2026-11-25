"""Run the EverResearch CLI selected by a plugin.

Use from a skill that requires an EverResearch command in the host's
execution environment. The runner installs into a private per-user cache.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import venv
from urllib.request import urlopen


def runtime_wheel():
    scripts = Path(__file__).resolve().parent
    shared = scripts.parent.parent / "maintain-project" / "scripts"
    lock = scripts / "rh-runtime.json"
    if lock.is_file():
        return pinned_wheel(lock, (scripts, shared))
    # Installers and earlier generated skills may already carry a local wheel.
    for directory in (scripts, shared):
        wheels = sorted(directory.glob("ever_research-*.whl"))
        if len(wheels) == 1:
            return wheels[0]
    raise RuntimeError("EverResearch runtime missing. Install the complete plugin package.")


def pinned_wheel(lock, local_directories):
    metadata = json.loads(lock.read_text(encoding="utf-8"))
    filename, digest, size = (metadata[key] for key in ("filename", "sha256", "size"))
    wheel_name = re.fullmatch(r"ever_research-([0-9]+(?:\.[0-9]+)+)-py3-none-any\.whl", filename)
    if (wheel_name is None or not re.fullmatch(r"[a-f0-9]{64}", digest)
            or type(size) is not int or size <= 0):
        raise RuntimeError("Invalid EverResearch runtime metadata.")
    cache = cache_directory() / "wheels" / digest
    for directory in (*local_directories, cache):
        wheel = directory / filename
        if (wheel.is_file() and wheel.stat().st_size == size
                and hashlib.sha256(wheel.read_bytes()).hexdigest() == digest):
            return wheel

    version = wheel_name.group(1)
    url = f"https://github.com/OpenSAE/EverResearch/releases/download/v{version}/{filename}"
    with urlopen(url, timeout=20) as response:
        contents = response.read(size + 1)
    if len(contents) != size or hashlib.sha256(contents).hexdigest() != digest:
        raise RuntimeError("The downloaded wheel does not match the plugin's runtime checksum.")
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as temporary:
        staged = Path(temporary) / filename
        staged.write_bytes(contents)
        destination = cache / filename
        staged.replace(destination)
    return destination


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
        wheel = runtime_wheel()
        rh = cli_environment(wheel)
        environment = os.environ.copy()
        environment["PATH"] = str(rh.parent) + os.pathsep + environment.get("PATH", "")
        environment["RH_PLUGIN_CLI"] = str(rh)
        environment["RH_PLUGIN_WHEEL"] = str(wheel)
        return subprocess.run([str(rh), *sys.argv[1:]], env=environment).returncode
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"EverResearch runtime unavailable: {error}", file=sys.stderr)
        return 78


if __name__ == "__main__":
    raise SystemExit(main())
