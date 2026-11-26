"""Run the project-owned single-device policy training task from the example."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tasks.training.single_device import main


if __name__ == "__main__":
    main()
