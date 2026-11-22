"""Use it. Python Standard library check the basic document structure of the project.

Only for project maintenance switches to run when they are closed. Check one level of responsibility, mandatory configuration and description,
Number of direct files in code directories and files in which items are dispersed.
"""

import json
import os
from pathlib import Path
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


def check():
    problems = []

    def fail(path, rule):
        problems.append({"path": path.relative_to(PROJECT).as_posix(), "rule": rule})

    for name in sorted(REQUIRED):
        path = PROJECT / name
        if path.is_symlink() or not path.is_dir():
            fail(path, "required_directory")

    for path in sorted(PROJECT.iterdir()):
        if path.name.startswith(".") or path.name == "__pycache__":
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
        if not any(p.stem == "config" and p.suffix in CONFIG_SUFFIXES
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
                    if entry.name.startswith(".") or entry.name == "__pycache__":
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
        path = PROJECT / ".researchharness" / "mode.toml"
        if path.parent.is_symlink() or path.is_symlink():
            raise ValueError("Maintaining switches must be a normal file within the project")
        mode = tomllib.loads(path.read_text(encoding="utf-8"))
        if mode != {"enabled": False} or type(mode.get("enabled")) is not bool:
            raise ValueError("Just... mode.toml Settings enabled = false Run offline check only when you want to")
        result = check()
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
