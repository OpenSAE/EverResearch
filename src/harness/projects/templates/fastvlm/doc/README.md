# FastVLM project guide

Install FastVLM and run image-prompt inference from the repository's main instructions. [Installation and inference](../README.md)

| Project path | Responsibility |
| --- | --- |
| `main.py`, `base/` | Source and installed commands, component coordination, and result I/O. [Call flow](code/README.md) |
| `conf/` | Inference options and encoder settings. [Configuration and overrides](conf.md) |
| `datasets/` | Local image reading and sample identity. [Input contracts](datasets.md) |
| `models/` | PyTorch checkpoints, vision encoders and language models. [Models and weights](models.md) |
| `tasks/` | Image-prompt generation, precheck, export, and inherited serving and training commands. [Task inputs and outputs](tasks.md) |
| `data/`, `scripts/` | Published checkpoint files and their download helper. [Checkpoint preparation](../data/README.md) |
| `experiment/` | Execution records, predictions and precheck reports. [Results and readback](experiment.md) |
| `assets/` | Figures, serving examples, upstream notices, MLX-VLM patch and original acceptance archive. [Project history](maintenance.md) |
| `third_party/apple_demo/` | SwiftUI demo, camera framework and Xcode project. [Xcode demo](../third_party/apple_demo/README.md) |
| `tests/`, `pyproject.toml`, `.github/workflows/` | Tests, package setup and continuous integration. [Environment and checks](environment/README.md) |
| `tmp/` | Short-lived local verification materials. |

[Apple Silicon export](code/apple_silicon/README.md) · [Maintenance record](maintenance.md)
