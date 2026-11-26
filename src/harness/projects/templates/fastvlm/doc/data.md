# FastVLM data and published checkpoints

## Purpose and main function

Locate the files that image prompting and supervised training read in a copied project.

## Scope of application

Use for published checkpoint installation, local image prompts and training data preparation.

Run `bash scripts/models/get_models.sh` from the project root to fetch Apple's published PyTorch checkpoints. The downloaded files retain the names provided by Apple.

The download helper writes to the shared workspace data directory. Use an explicit checkpoint with `--model-path` when working with another cache. The [checkpoint guide](environment/checkpoints.md) describes the available weights. The [dataset guide](datasets.md) describes image and supervised input contracts.
