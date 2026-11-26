"""Check types under the same Python package names used by installed LeRobot."""

import os
from pathlib import Path
import subprocess  # nosec B404
import sys
from tempfile import TemporaryDirectory


PROJECT = Path(__file__).resolve().parents[2]


def main() -> int:
    """Assemble the relocated modules and run mypy on the assembled package."""
    with TemporaryDirectory() as package_dir:
        subprocess.run(  # nosec B603
            [sys.executable, "setup.py", "build_py", "--build-lib", package_dir],
            cwd=PROJECT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        environment = {**os.environ, "MYPYPATH": package_dir}
        return subprocess.run(  # nosec B603
            [
                sys.executable, "-I", "-m", "mypy", "--config-file=pyproject.toml",
                str(Path(package_dir, "lerobot")), "scripts/ci", "scripts/development", "tests/fixtures/doctest_config.py", "setup.py",
            ],
            cwd=PROJECT,
            env=environment,
            check=False,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
