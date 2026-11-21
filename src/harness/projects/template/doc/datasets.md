# Data Set

## Purpose

Describes the data, samples and classifications that can be readable for the classification tasks.

## Scope

The data conditions used to prepare the sorting input, select offline samples or explain the experiment.

## Purposes and access

Use `--set dataset=<id>` in the YaML formulation. See [data entry](../datasets/plugins.py) for registration.

## Shared Parameters

`dataset.image_size` is the edge length of the output image, `training.seed` is a random feed for the item. See [parameter](conf.md) (for the configuration file, default value and overwhelming rules, see default values and effects for `training.batch_size`).

## Component

### `cub200`

- **function**. Use CUB-200-2011 for categorizing 200 species of birds.
- **Selection Method**. `--set dataset=cub200`, use the decompression data catalogue.
- **Enter and produce**. Loading RGB images by official labels and dividing, returning to training, testing, and training for certainty.
- The specific parameter **is**. `dataset.root` or `--data-root` points to a directory containing images and official marked files. The default image size is 224 pixels.
- **Validation basis**. [read to achieve](../datasets/cub200/dataset.py) and [data disaggregation check](../tests/test_boundaries.py)].

### `synthetic`

- **function**.
- **Selection Method**.`--set dataset=synthetic`.
- **Enter and produce**. Generate 12 RGB scales and digital labels from random seeds, the first 8 entered as training and the last 4 entered as testing.
- **Specific Parameters**.The default image size is 32 Pixels, input provided by generator.
- **Validation is based on**. [Samps are generated](../datasets/cub200/offline_samples.py) and [outline precheck records](experiment.md) (used for random initialization and fine-tuning of respective conditions based on real-life checks).
