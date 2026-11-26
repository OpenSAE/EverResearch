"""Run the CoTracker checkout with its assets and configuration."""

from pathlib import Path

from cotracker.commands import main


if __name__ == "__main__":
    raise SystemExit(main(default_workspace=Path(__file__).resolve().parent))
