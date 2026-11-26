# LeRobot environment

## Purpose and main function

Set up the Python environment and check the commands used for local maintenance.

## Scope of application

Use these commands from the project root for setup, or run the installed commands from any working directory. Choose simulator and robot extras only for the workflow that uses them.

LeRobot requires Python 3.12 or later. Install the locked dependencies with `uv sync --locked`. For training and dataset work, run `uv sync --locked --extra training --extra test`. Video operations require FFmpeg. For policy evaluation, also install the named simulator and the evaluation extra. See the [installation reference](../code/reference/source/installation.mdx) for platform-specific instructions.

Run `uv run lerobot-info` and `uv run lerobot-train --help` to check the installed commands. With a local LeRobot dataset, preview the ACT example using:

```sh
uv run lerobot-precheck --config_path=conf/config.yaml --dataset.root=/path/to/dataset --output_dir=/path/to/output
```

The preview resolves the same options and admission checks as the training command. It prints the selected dataset, model, device, and output location. Use `lerobot-train` with the same arguments to open the dataset and run the single configured training step. The project's default training settings remain available when invoking the command without the example configuration.

Run `uv run pytest tests -m base` for the base test tier. Run `python -IS .everresearch/maintain.py status` to see the connected maintenance source.
