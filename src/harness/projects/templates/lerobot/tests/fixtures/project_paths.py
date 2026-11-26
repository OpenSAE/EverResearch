"""Paths shared by LeRobot's checkout-based test fixtures."""

from pathlib import Path

import lerobot

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(lerobot.__file__).parent
ARTIFACTS = PROJECT_ROOT / "tests/fixtures/artifacts"
