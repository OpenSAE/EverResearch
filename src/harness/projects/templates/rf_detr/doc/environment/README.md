# RF-DETR development and execution environment

## Purpose

Use this page to prepare a checkout for local configuration previews, product tests and training. The experiment records retain the environment used for each run.

## Scope

These commands target the RF-DETR source checkout. The published [installation guide](../code/website/source/getting_started/install.md) covers the supported Python versions and optional deployment backends.

## Checkout setup

Use Python 3.10 or later. Run the following from the repository root to prepare the development environment and install the dependencies used by the CPU test job.

```bash
uv venv
uv pip install -e '.[train,augment,cli,visual,data]' --group tests --torch-backend=cpu
```

Use the appropriate PyTorch build for GPU training. This checkout was checked with `.venv/bin/python`, Python 3.12.15 and PyTorch 2.15.0+cu132 on a GeForce RTX 5090. Choose the accelerator with a Lightning trainer override, such as `--trainer.accelerator=cpu` or `--trainer.accelerator=gpu`.

Set `--model.train_config.init_args.dataset_dir` to a prepared dataset root and `--model.train_config.init_args.dataset_file` to its format. The [dataset guide](../code/website/source/learn/train/dataset_formats.md) describes the annotation and split layout. To use an existing model checkpoint, pass its path using the recipe's `pretrain_weights` option or the trainer's `--ckpt_path` for a full Lightning checkpoint.

## Bounded checks

```bash
.venv/bin/python -m rfdetr fit --config rfdetr_nano --print_config
.venv/bin/python -m pytest --collect-only
.venv/bin/python -m pytest tests/test_train_experiment.py
```

The configuration preview resolves the recipe and overrides before constructing a model or opening a dataset. Use the [experiment guide](../experiment.md) to retrieve the command, package versions and artifacts from a retained execution.
