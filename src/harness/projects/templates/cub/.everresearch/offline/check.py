"""Check the basic structure of an offline project using the standard library.

The Git path selection is also used by the central structural checker.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib


PROJECT = Path(__file__).absolute().parents[2]
REQUIRED = {"base", "datasets", "models", "tasks", "conf", "doc"}
OPTIONAL = {"experiment", "tests", "scripts", "assets", "tmp", "third_party"}
ROOT_FILES = {
    "README.md", "AGENTS.md", "LICENSE", "LICENSE.txt", "LICENSE.md",
    "NOTICE.md", "NOTICE.txt", "CITATION.cff", "CHANGELOG.md", "CONTRIBUTING.md",
    "pyproject.toml", "setup.py", "setup.cfg", "main.py", "Makefile", "CMakeLists.txt",
    "Cargo.toml", "package.json", "uv.lock", "poetry.lock", "pytest.ini",
}
CONFIG_SUFFIXES = {".yaml", ".yml", ".toml", ".json"}


def project_paths(root):
    """Select tracked files, eligible new files, and their parent directories."""
    if not (root / ".git").exists() or shutil.which("git") is None:
        return None
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
         "--exclude=__pycache__", "--exclude=*.py[co]", "--exclude=*.egg-info"],
        cwd=root, capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(f"Could not list Git project files: {os.fsdecode(result.stderr).strip()}")
    paths = set()
    for name in result.stdout.split(b"\0"):
        if name:
            path = root / os.fsdecode(name)
            if path.exists() or path.is_symlink():
                paths.add(path)
                paths.update(parent for parent in path.parents if parent.is_relative_to(root))
    return paths


def check():
    problems = []
    paths = project_paths(PROJECT)

    def included(path):
        return paths is None or path in paths

    def fail(path, rule):
        problems.append({"path": path.relative_to(PROJECT).as_posix(), "rule": rule})

    for name in sorted(REQUIRED):
        path = PROJECT / name
        if path.is_symlink() or not path.is_dir():
            fail(path, "required_directory")

    for path in sorted(PROJECT.iterdir()):
        if not included(path) or path.name.startswith(".") or path.name == "__pycache__":
            continue
        if path.is_symlink():
            if path.name not in REQUIRED | OPTIONAL | ROOT_FILES:
                fail(path, "root_path")
        elif path.is_dir():
            if path.name not in REQUIRED | OPTIONAL:
                fail(path, "root_directory")
        elif (path.name not in ROOT_FILES
              and not (path.name.startswith("requirements") and path.suffix == ".txt")):
            fail(path, "root_file")

    conf = PROJECT / "conf"
    if not conf.is_symlink() and conf.is_dir():
        if not any(included(p) and p.stem == "config" and p.suffix in CONFIG_SUFFIXES
                   and not p.is_symlink() and p.is_file() for p in conf.iterdir()):
            fail(conf, "configuration_entry")

    doc = PROJECT / "doc"
    if not doc.is_symlink() and doc.is_dir():
        for name in ("README.md", "environment/README.md"):
            path = doc / name
            if path.parent.is_symlink() or path.is_symlink() or not path.is_file():
                fail(path, "required_documentation")

    for top in ("base", "tasks", "scripts", "tests"):
        tree = PROJECT / top
        if tree.is_symlink() or not tree.is_dir():
            continue
        pending = [tree]
        while pending:
            directory = pending.pop()
            files = 0
            with os.scandir(directory) as entries:
                for entry in entries:
                    if not included(Path(entry.path)) or entry.name.startswith(".") or entry.name == "__pycache__":
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        pending.append(Path(entry.path))
                    else:
                        files += 1
            if files > 15:
                fail(directory, "direct_file_count")

    return {"mode": "offline", "passed": not problems, "violations": problems}


def main():
    try:
        path = Path(__file__).absolute().parents[1] / "mode.toml"
        if path.parent.is_symlink() or path.is_symlink():
            raise ValueError("Expected a regular maintenance mode file inside the project.")
        mode = tomllib.loads(path.read_text(encoding="utf-8"))
        if mode != {"enabled": False} or type(mode.get("enabled")) is not bool:
            raise ValueError(f"Set enabled = false in {path} to run the offline checker.")
        result = check()
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
