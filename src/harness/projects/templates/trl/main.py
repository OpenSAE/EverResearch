"""Launch the maintained TRL experiment from a checked project configuration.

Run a supported recipe with an automatic gate, or run the gate alone to check
the actual dataset, model, and trainer on this machine.
"""

from base.experiment_runner import main


if __name__ == "__main__":
    raise SystemExit(main())
