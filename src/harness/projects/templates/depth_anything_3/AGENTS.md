# Project maintenance

## Purpose and main functions

Use this reference to find the project entry points and maintain their dependencies.

## Scope

Applies to work on this template. Start with README.md and doc/README.md for normal commands and setup.

<!-- everresearch:search -->
## Locate projects and files

Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.
<!-- /everresearch:search -->

<!-- everresearch:mode -->
## Choose the maintenance mode

### Purpose and main functions

Use the project setting to select its maintenance guide and structure checker.

### Scope

Use this section for project maintenance, checking the online connection, or running an offline structure check.

Start by reading `.everresearch/mode.toml`. Its `enabled` setting selects this project's maintenance mode. Follow the user's choice and obtain authorization before changing it.

- **`enabled = false` selects offline maintenance.** Use the project's [offline operations guide](.everresearch/offline/operations.md). It explains how to plan, carry out, and finish maintenance using the project's files, commands, tests, and data.
- **`enabled = true` selects online maintenance.** Run `python -IS .everresearch/maintain.py status` first. When it prints `online`, read the central guide at the reported path. Follow that guide to the operations manual, shared skills, and central checks in the EverResearch repository. If the status command fails, report the cause and pause work that requires central maintenance until the user restores the connection or selects offline mode.
- **A missing or invalid setting blocks maintenance.** Report the problem and continue once the setting has been corrected or the user has chosen a mode.

When a structure check is authorized, run `python -IS .everresearch/maintain.py check` from the project root. The command runs the checker for the selected mode. Follow the project README for installation, training, prechecks, and reading results.
<!-- /everresearch:mode -->

## Original project and template layout

- **Original project** [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3)
- **Source revision** [3d835ec1a5802d64a8b8b15f817a1ab54809bfe4](https://github.com/ByteDance-Seed/Depth-Anything-3/tree/3d835ec1a5802d64a8b8b15f817a1ab54809bfe4)
- **Paper** [Depth Anything 3: Recovering the Visual Space from Any Views](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e4cd50120b6d7e8daff1749d6bbaa889-Abstract-Conference.html) · ICLR 2026 Oral
- **Authors** Haotong Lin, Sili Chen, Jun Hao Liew, Donny Y. Chen, Zhenyu Li, Yang Zhao, Sida Peng, Hengkai Guo, Xiaowei Zhou, Guang Shi, Jiashi Feng, Bingyi Kang
- **Original source archive** [depth_anything_3.zip](third_party/upstream/depth_anything_3.zip)
- **Archive SHA-256** `a19b31f64ed11d5c38438ea0f3e0864eecc299044967026749304c3a03dcf053`

The archived backend revision matches the retained dashboard renderer in [the reorganized backend](base/depth_anything/services/server.py).

### Before organization

```text
Depth-Anything-3/
├── .flake8
├── .gitattributes
├── .gitignore
├── .gitmodules
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── assets/
│   ├── examples/
│   └── images/
├── da3_streaming/
│   ├── README.md
│   ├── configs/
│   ├── da3_streaming.py
│   ├── fastloop/
│   ├── loop_utils/
│   └── … (3 more entries)
├── docs/
│   ├── API.md
│   ├── BENCHMARK.md
│   ├── CLI.md
│   └── funcs/
├── notebooks/
│   └── da3.ipynb
├── pyproject.toml
├── requirements.txt
└── src/
    └── depth_anything_3/
```

### After organization

```text
depth_anything_3/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .flake8
├── .gitattributes
├── .gitignore
├── .package/
│   └── depth_anything_3/
├── .pre-commit-config.yaml
├── AGENTS.md
├── LICENSE
├── README.md
├── assets/
│   ├── examples/
│   └── media/
├── base/
│   └── depth_anything/
├── conf/
│   ├── config.yaml
│   ├── models/
│   └── tasks/
├── datasets/
│   ├── benchmark/
│   └── media/
├── doc/
│   ├── README.md
│   ├── base.md
│   ├── code/
│   ├── conf.md
│   ├── datasets.md
│   └── … (5 more entries)
├── models/
│   ├── backbone/
│   └── model/
├── pyproject.toml
├── requirements.txt
├── requirements_streaming.txt
├── scripts/
│   ├── inference.ipynb
│   └── streaming/
├── tasks/
│   ├── evaluation/
│   ├── inference/
│   ├── precheck/
│   └── streaming/
├── tests/
│   ├── test_gallery_results.py
│   └── test_inference_cli.py
└── third_party/
    └── upstream/
```
