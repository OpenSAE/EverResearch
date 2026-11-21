# Training recipes and overrides

## Purpose

This page explains how the RF-DETR checkout selects and applies a named Lightning configuration.

## Configuration entry point

[conf/config.yaml](../conf/config.yaml) lists dataset, model and task identities under `catalogs`. Under `recipes`, it stores the RF-DETR Base, Nano, Small, Medium and Large detection examples and six segmentation variants.

Register a new dataset or custom model identity in `catalogs` when using it for ongoing runs. The layout check uses that identity to recognize the corresponding experiment directory.

The installed training CLI reads either a Lightning YAML file provided by the caller or a recipe name from the checkout. For example:

```bash
python -m rfdetr fit --config rfdetr_nano --print_config
```

Arguments after the recipe override its values through Lightning’s configuration parser. The `--print_config` option prints the effective configuration before loading a dataset or model. Existing checkout CLI commands using `--config configs/rfdetr_nano.yaml` resolve to the same recipe. An existing user-supplied configuration file takes precedence over the compatibility lookup.

[Training parameters](code/website/source/learn/train/training_parameters.md) documents dataset, optimizer, augmentation, evaluation and logging options. [Training recipes and paths](code/website/source/resources/project_structure.md#preview-a-training-experiment) shows how to preview a named execution with data and hardware overrides.
