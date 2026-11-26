# CUB-200 template maintenance

## Purpose and main function

Explain how the CUB-200 reference template validates classification, configuration and saved runs.

## Scope of application

Use this guide when copying the template, reviewing its entry points, or preparing a bounded or full classification run.

| Area | Source and check |
| --- | --- |
| Dataset | `datasets/` owns the CUB-200 reader and the synthetic generator. Verify CUB-200 with the published images, labels and split. |
| Model | `models/` owns the ResNet and small convolutional variants. The configuration selects them by name. |
| Task | `tasks/` owns classification and precheck. The installed `cub_template` command handles precheck, execution and saved run readback. |
| Configuration and outputs | [Configuration options](conf.md) and [experiment records](experiment.md) explain the effective recipe and artifacts. |

## Verify a copied template

Run `python -IS .everresearch/maintain.py check` and follow the [synthetic CPU example](../README.md#run-a-small-synthetic-experiment). Read the saved result with `python -m cub_template inspect <run-directory>`. The synthetic recipe exercises the task, reader, model and result writer. Use the official CUB-200 split and weights required by your selected recipe for a real-data check.

## Formal run choices

The [CUB-200 training section](../README.md#use-cub-200-data) uses the published CUB-200 train and test split and the ResNet18-based baseline. It writes training metrics and a checkpoint. Use the [baseline recipe](../experiment/cub200/residual_classifier/classification/scratch_baseline/recipe.toml) to review the workload. Measure the actual model and batch in a trial of about ten examples or five minutes before estimating the full training time.
