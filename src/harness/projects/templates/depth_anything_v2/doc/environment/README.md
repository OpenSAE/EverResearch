# Environment and verification

## Purpose and main function

Install the research command, identify its model weights and optional dependencies, and run a small verification.

## Scope of application

Use these instructions from the project root. Inference can use CUDA, MPS, or CPU. Distributed training uses CUDA and NCCL.

Install with Python 3.11 or later. Select a PyTorch build compatible with your hardware. The install helper builds from a temporary copy so installation keeps the project tree clean.

```bash
bash scripts/install_project.sh
```

Pass `training`, `pointcloud`, or `demo` to install optional dependencies. You can combine them as `training,pointcloud,demo`.

Activate your isolated environment and point the project at a directory containing the official weights.

```bash
export DEPTH_ANYTHING_WEIGHTS="${DEPTH_ANYTHING_WEIGHTS:-$PWD/../data/depth_anything_v2/checkpoints}"
python -IS .everresearch/maintain.py status
python -IS .everresearch/maintain.py check
depth-anything image --encoder vits --img-path assets/samples/images/files/demo01.jpg --precheck
```

The Small, Base, and Large checkpoints for relative, indoor metric, and outdoor metric depth can be placed there. Outdoor predictions take an explicit `--load-from` path and typically use `--max-depth 80`. See the [project guide](../README.md) and [metric workflows](../models.md) for checkpoint sources and inference options. For a command run from another directory, pass `--workspace /path/to/project` before the subcommand and use paths relative to the current directory or absolute paths for explicit inputs.

Use `--precheck` on an inference, demo, or training command to run a small check without starting the full job. Inference checks one image or the first video frame and reopens the output. The demo checks a bundled example and its download formats. The training precheck requires one available CUDA GPU and runs an isolated optimizer step and validation sample using the supplied splits and weights. The JSON report lists the effective inputs, samples checked, outputs read, and timings. Normal launches run the same check automatically. Managed inference and training runs save the report under `reports/precheck.json`.
