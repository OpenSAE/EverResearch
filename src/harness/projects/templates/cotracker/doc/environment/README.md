# CoTracker environment

## Purpose and main function

Describe the interpreter, dependencies, example video, and checkpoints needed to run CoTracker.

## Scope of application

Use this guide to set up a checkout and choose dependencies for tracking, evaluation, training, or demos.

Install the project in an isolated Python environment with a PyTorch build that supports your device. For tracking, run `python -m pip install -e '.[dev]'`. Add `evaluation` to the extras to use the benchmark command. Run `python -m pytest -q` to check the bilinear sampling implementation.

The included apple clip requires no download. The standard model is CoTracker3 scaled offline. Give `--checkpoint` an absolute path to its released weight file to run locally without network access. Set `COTRACKER_OFFLINE_CHECKPOINT` to reuse one local checkpoint across commands. With no override, the local model factory retrieves the released weights through PyTorch's checkpoint cache.

Set `COTRACKER_WEIGHTS` to the directory containing the official checkpoints. Choose an isolated interpreter with a compatible PyTorch and video stack. TAP-Vid, Dynamic Replica, annotated Kubric, and a custom real-video dataset are separate inputs for benchmark and training workflows.

The original training runners require a Lightning version with `pytorch_lightning.lite.LightningLite`, TensorBoard, OpenCV, and additional dependencies documented in the project README. The real-video runner also requires TAPIR and its checkpoint. Set `COTRACKER_TAPIR_CHECKPOINT` to the local panning checkpoint. The Slurm scripts require the partition and account settings of the original training environment.
