# CoTracker configuration

## Purpose and main function

Describe the options consumed by the project command and Hydra evaluation.

## Scope of application

Use this page to choose input, device, tracking settings, and benchmark presets.

[Tracking defaults](../conf/config.yaml) select the example clip, a 10-by-10 grid, query frame zero, forward tracking, and automatic device selection. Command-line options override the defaults. `--print-config` prints the effective values without loading the model.

[Evaluation presets](../conf/tasks/evaluation/presets.yaml) retain the original Hydra preset names and dataset values. Select one with `evaluate --config-name NAME` and pass Hydra overrides for the dataset root, checkpoint, and experiment directory.
