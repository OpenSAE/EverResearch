# Commands and installed APIs

## Purpose and main function

Locate dispatch, configuration loading, and public Python entry points.

## Scope of application

Use this page when running the project or maintaining compatibility after a move.

`python main.py`, `python -m cotracker`, and `cotracker` use the same [command dispatcher](../base/tracking/commands.py). The checkout launcher uses its own directory by default. The installed command uses the current directory unless you pass `--workspace`.

[Packaging](../setup.py) maps the original `cotracker` imports to implementations under `base`, `datasets`, `models`, and `tasks`. Local PyTorch Hub factory calls now use `cotracker.hub_api` directly.
