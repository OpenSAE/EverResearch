---
description: RF-DETR checkout structure, training entry points, and experiment records.
---

# Project structure and training experiments

## Purpose

This page maps the RF-DETR checkout to its public commands, configuration, component implementations, test suite, and training results. It also describes the named training launcher available in a source checkout.

## Scope

Use this page when changing the checkout, choosing a command, or finding and reproducing a training execution. The [installation guide](../getting-started/install.md) describes supported installs, and the [training guide](../learn/train/index.md) covers the Python training API and available metrics.

## Checkout layout

| Location | Responsibility and consumer |
| --- | --- |
| `base/detector/interfaces/command_line/`, `__main__.py` | Console script and module entry point. `fit`, `validate`, `test`, and `predict` use the training CLI. `python -m rfdetr.cli.webdataset` packs annotated data for streaming. |
| `base/detector/config.py`, `base/detector/runtime/` | Pydantic model and training configurations and the model builder's resolved arguments. `conf/config.yaml` provides YAML examples for Lightning CLI, and `pyproject.toml` declares installation and development dependencies. |
| `datasets/detection_data/` | Dataset dispatch and implementations for official COCO, Objects365, Roboflow exports, YOLO, and WebDataset. Augmentation and annotation readers live with the dataset code. See [dataset formats](../learn/train/dataset-formats.md) for the expected layouts and split names. |
| `models/detection_transformers/`, `base/detector/variants.py`, `base/detector/interfaces/assets/` | Model composition, backbones, detection and extra heads, weight loading, public variant classes, default weight names, and COCO labels. |
| `tasks/train/`, `tasks/evaluation/` | Lightning model and data modules, trainer construction, checkpointing, metrics, and evaluators. The training DataModule selects the data builder and constructs the split loaders. See the [custom training API](../learn/train/customization.md) for these entry points. |
| `base/detector/detector.py`, `base/detector/inference.py`, `base/detector/interfaces/prediction/` | Public model and inference interfaces plus shared preprocessing, batching, postprocessing, and media input handling. See [inference](../learn/inference.md) for prediction inputs and outputs. |
| `base/detector/interfaces/export/`, `base/detector/runtime/platform/`, `base/detector/interfaces/visualize/`, `base/utilities/` | Deployment artifacts and their runtime adapters, Roboflow integration, display of data and results, and shared support. See the [export guide](../exports/index.md) for target format and runtime requirements. |
| `scripts/` | Checkout operations. `train_experiment.py` launches and reads named training executions. `update_weekly_metrics.py` services the repository metrics workflow. |
| `tests/`, `.github/` | Pytest coverage organized by package responsibilities, synthetic test input, and historical checkpoint compatibility. GitHub workflows define the test and release commands. |
| `doc/code/website/source/`, `assets/documentation/`, `scripts/documentation/` | MkDocs content, notebooks, assets, and published navigation. The root README, change history, license, citation, and contributor instructions provide repository-level context. |
| `experiment/` | Generated execution records, metrics, and checkpoints from the checkout launcher. The launcher creates the directory when a training execution starts. |

The package layout supports installed `rfdetr.*` imports. Example configurations remain in `conf/config.yaml`, where the public commands and configuration round-trip tests find them. Tests for a package component live in the corresponding test folder. Export formats and prediction, model, and training internals use their existing nested groups. The checkout can also contain optional `.agents/skills/` entries from ResearchHarness.

## Preview a training experiment

Install the checkout and its training and CLI requirements with `pip install -e '.[train,cli]'`. The launcher uses the `rfdetr_nano` detection recipe by default. Pass another recipe with `--config` before `--`. Options after `--` go to `python -m rfdetr fit` and override the recipe through Lightning's normal parsing rules.

```bash
python scripts/train_experiment.py fit --dataset coco --name default_finetuning --plan -- \
  --model.train_config.init_args.dataset_dir /data/coco \
  --model.train_config.init_args.dataset_file coco \
  --model.model_config.init_args.num_classes 90
```

`--dataset` names the actual data collection for result navigation. `dataset_file` selects the reader, so official COCO needs `coco`, while a Roboflow-format COCO export uses `roboflow`. Official COCO retains category IDs through 90, so the example restores the pretrained Nano classifier size. A remapped custom export uses its mapped class count. The source path and the recipe path provided on the command line resolve from the current working directory. The experiment path resolves from the checkout. `--name` uses one to three lowercase words separated by underscores and describes the training purpose.

The plan prints the parsed configuration and the experiment path without creating an execution or loading data or weights. With `--plan` omitted, the launcher calls `fit`, setting both the RF-DETR output directory and Lightning root to the execution’s `artifacts/` directory.

## Read results and resume

```bash
python scripts/train_experiment.py results experiment/coco/rfdetr_detection_nano/train/default_finetuning
```

Pass the named experiment directory to list executions or a specific execution directory to read its record. Results list the active or final status, parsed fit configuration, precheck outcome, environment versions, command, and artifact paths relative to the `directory` field. A normal fit can produce `config.yaml`, `metrics.csv`, and checkpoints such as `last.ckpt`. TensorBoard event files are in `logs/tensorboard/`. Exact outputs depend on the recipe and trainer options. The [training guide](../learn/train/index.md#result-checkpoints) explains checkpoint types and validation metrics.

A named fit first runs Lightning's fast development mode with the same selected model and data and one batch per active phase. Run the check on its own by replacing `fit` with `precheck` and passing the same recipe and arguments. A failure records the original diagnostic and stops the named launch before formal training.

Repeated commands create distinct execution directories for the same purpose. Pass `--ckpt_path` after `--` to start a new execution from a previous Lightning checkpoint. The original run and its artifacts remain available at the previous execution path.

The `rfdetr fit`, `rfdetr validate`, `rfdetr test`, and `rfdetr predict` commands also check the selected task with one batch per active phase before starting the full command. Use `rfdetr precheck validate` with your validation options, for example, to print the check result on its own. Use the normal task command to run with a caller-managed output directory. Python calls such as `RFDETR.train()` use their own data and model setup.

The loader also resolves the original COCO subset experiment addresses. It returns the individual run’s current artifact location and preserves the configuration and working directory recorded when that run executed.
