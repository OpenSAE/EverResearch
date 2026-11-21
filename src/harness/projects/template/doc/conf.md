# Configure Parameters

## Purpose

Explain how the parameter reaches the actual consumer, how the default works, how it is covered and read back the effective value.

## Scope

This is used to use the current template formulation and to maintain open parameters. History is based on current snapshots.

## Configure Entry and Entry Orders

`python -m cub_template run --subname <Test Name>` Read [Default Formula](../conf/config.yaml).`--config` Specifies the input formulation. YAML Default group and formulation by Hydra Synth,`--set` You can replace a component group or overwhelm a field. Fields other than the component preset are supplemented by a syntax, such as: `--set +model.hidden_dim=32`.The return value of the model statement is merged before construction, with a visible value given priority. TOML The experimental formula is read directly and the parameters are written in the formula.`--data-root` Priority is given to the directory in the data configuration. The active configuration is written to the active directory by the official running. `config.yaml`,The list. `effective_config` Point it. The sub-command also selects the corresponding task process. See [Command entrance](../base/cub_template/cli.py)and [Configure Parsing](../base/cub_template/runtime/config.py).

## Parameter Description

### `dataset`

Select the image source. Default `cub200` to read real bird images. `synthetic` is a random seed that produces small image samples to check the entry. Switch with `--set dataset=synthetic`. See [Dataset](datasets.md) for data selection, splits, and synthetic inputs.

### `model`

Select the model and its default parameters. Default `resnet18_mlp`. Subclasses and CNN see [Models](models.md) for variants, classifier head widths, and weights. Switching through `--set model=<id>`.

### `task`

Select the task identifier. Default `classification`. precheck and compare sub-commands can select the corresponding process. See [Target](tasks.md) for selection and access to the product, for official classification and for the use of precheck.

### `dataset.image_size`

Specifies that the RGB image is long, integer and at least 32 pixels. CUB defaults 224, synthesizes 32. Changes change the calculation and preprocess output. See [Input check](../base/cub_template/contracts.py).

### `dataset.root`

Specifies the CUB data decompression directory, with the default relative formula position `../data/CUB_200_2011`. The command line `--data-root` gives priority to a synthetic formulation provided by the generator.

### `model.hidden_dim`

ResNet18 Header hides the width, positive integer. The default version is 256, and the small head is 16. The weight shape changes after overwhelming.

### `model.channels`

Small CNN volume output channels, positive integer, default 16. Overwrite changes the shape of the amount of the volume and the parameter of the header.

### `model.initialization`

ResNet18 is currently receiving `random`, which is also omitted at random. Historic pre-training records are interpreted using the corresponding source code.

### `task.target`

Prechecks and performance compares the targets to be checked. Default `classification`. Take the current tasks from the other tasks when they are launched.

### `runtime.device`

Select `auto`, `cpu` or `cuda`, by default `auto`, by the availability of the equipment. The actual device is saved with the running list.

### `runtime.workers`

Images load process numbers, non-negative integers, default 2. Read by the main process when set to 0, affecting loading performance.

### `runtime.cpu_threads`

PyTorch uses CPU threads, positive integers, default 4. Changes can affect the current resources and time-consuming.

### `training.seed`

random seeds, non-negative integers, default 42, for training in random operation and synthetic image generation.

### `training.batch_size`

The number of samples per training batch, at least 2 integers, default 32. Changes affect the amount of samples per step and memory.

### `training.epochs`

Maximum number of training rounds, integer at least 1, default 30.

### `training.learning_rate`

The learning rate for AdamW, with a limited positive number, is default 0.001.

### `precheck.samples`

The number of samples that are scheduled for a single pre-test is at least 2 integer, default 2. The actual workload is limited by both batch size and available samples.

### `benchmark.samples`

Number of performance-comparison samples, integers at least 2, default 32. Actual comparison is limited by the amount of data.

### `benchmark.warmup`

The number of preheats, non-negative integers, default 1. The preheats are not included in the statistics.

### `benchmark.repeats`

Number of times each performance candidate is counted at least 2 integer, default 3.

### `benchmark.max_cuda_memory_fraction`

CUDA's more visible budget ratio, which is greater than 0 to 1, with default 0.9.

### `benchmark.candidate_workers`

The number of loads that you want to compare with the baseline is not negative and is different from the baseline. If the baseline is not configured, the baseline is 0, or 0.

### `--candidate-workers`

Specifies the number of candidate processes to be used for this comparison, with priority given to `benchmark.candidate_workers` in the formulation.

### `--subname`

Specifies a name for the experiment. Requires that one to three words describing the use be completed in a visible format, and the results are archived with that name.

### `--config`

Specifies the location of the item YAML or the existing TOML formulation. Use the project default formulation when not specified.

### `--set`

This operation overwrites a configuration value and can be repeated. Formats are `group=value` or `full-parameter-name=value`. New fields in YAML need to be added.

### `--data-root`

Transmit CUB data directories visible to this operation, with priority over `dataset.root`.
