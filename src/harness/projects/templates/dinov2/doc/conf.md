# DINOv2 configuration

## Purpose and main function

Find the DINOv2 defaults, shipped presets and configuration arguments.

## Scope of application

Use these configuration choices with a DINOv2 training, evaluation or precheck entry point.

The package loads the [original defaults](../conf/config.yaml) and merges the selected
configuration on top. User overrides are applied by the same launchers. Supply a path to a
YAML file or a bundled identifier to `--config-file`, for example
`train/vitl16_short`, `eval/vits14_pretrain`, or `eval/cell_dino/vitl16_pretrain`.
The [training presets](../conf/tasks/training/config.yaml) and
[classification presets](../conf/tasks/classification/config.yaml) list all identifiers.
References to the original bundled `dinov2/configs/...yaml` paths are accepted by the
configuration loader. YAML files written by earlier runs remain readable through the
same `--config-file` argument.
