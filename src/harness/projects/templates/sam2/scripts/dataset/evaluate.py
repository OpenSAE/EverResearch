"""Run the project's evaluate command from a checkout."""
from pathlib import Path
from runpy import run_path

if __name__ == "__main__":
    checkout = Path(__file__).resolve().parents[2]
    run_path(str(checkout / "main.py"))["enable_checkout_imports"]()
    from sam2.evaluation.evaluator import main

    main()
