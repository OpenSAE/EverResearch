"""Run the project's train command from a checkout."""
from pathlib import Path
from runpy import run_path

if __name__ == "__main__":
    checkout = Path(__file__).resolve().parents[2]
    run_path(str(checkout / "main.py"))["enable_checkout_imports"]()
    from training.train import cli

    cli()
