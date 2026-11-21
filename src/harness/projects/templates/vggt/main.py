"""Run VGGT commands directly from a source checkout."""

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent / "base"))
from geometry_runtime.commands import main

if __name__ == "__main__":
    main()
