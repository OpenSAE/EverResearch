# Maintain Depth Anything V2

## Purpose and main function

Keep this depth estimation template runnable through its documented commands.

## Scope of application

Use these instructions when maintaining the template and verifying its relative and metric depth workflows.

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

## Verify changes to the depth workflows

Use the [project guide](doc/README.md) to find the owning model, dataset, or task and its current public command. The [environment guide](doc/environment/README.md) gives the installed command, inference weights, and precheck. The [maintenance record](doc/maintenance.md) identifies what was checked against the original source.

## Original project and template layout

- **Original project** [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)
- **Source revision** [a561b849ebae10a6f5ef49e26c83cbbcd36c71bf](https://github.com/DepthAnything/Depth-Anything-V2/tree/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf)
- **Paper** [Depth Anything V2](https://proceedings.neurips.cc/paper_files/paper/2024/hash/26cfdcd8fe6fd75cc53e92963a656c58-Abstract-Conference.html) · NeurIPS 2024
- **Authors** Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiaogang Xu, Jiashi Feng, Hengshuang Zhao
- **Original source archive** [depth_anything_v2.zip](third_party/upstream/depth_anything_v2.zip)
- **Archive SHA-256** `0022639d5b23499329ca4fd29a92993e86b52fdfe9aaf21df683383136e91b65`

### Before organization

```text
Depth-Anything-V2/
├── DA-2K.md
├── LICENSE
├── README.md
├── app.py
├── assets/
│   ├── DA-2K.png
│   ├── examples/
│   ├── examples_video/
│   └── teaser.png
├── depth_anything_v2/
│   ├── dinov2.py
│   ├── dinov2_layers/
│   ├── dpt.py
│   └── util/
├── metric_depth/
│   ├── README.md
│   ├── assets/
│   ├── dataset/
│   ├── depth_anything_v2/
│   ├── depth_to_pointcloud.py
│   └── … (5 more entries)
├── requirements.txt
├── run.py
└── run_video.py
```

### After organization

```text
depth_anything_v2/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitignore
├── AGENTS.md
├── LICENSE
├── README.md
├── assets/
│   ├── illustrations/
│   ├── samples/
│   └── splits/
├── base/
│   ├── __main__.py
│   ├── commands.py
│   ├── dist_helper.py
│   ├── logging_setup.py
│   └── records.py
├── conf/
│   └── config.toml
├── datasets/
│   ├── da_benchmark/
│   ├── hypersim_images/
│   ├── kitti_images/
│   ├── media/
│   ├── transforms/
│   └── … (1 more entries)
├── doc/
│   ├── README.md
│   ├── data.md
│   ├── environment/
│   ├── maintenance.md
│   └── models.md
├── models/
│   └── depth_anything_v2/
├── pyproject.toml
├── requirements.txt
├── requirements_metric.txt
├── scripts/
│   ├── distributed_training.sh
│   ├── evaluate_depth_order.py
│   ├── install_project.sh
│   └── run_demo_batch.py
├── tasks/
│   ├── demo/
│   ├── image_depth/
│   ├── pairwise_depth/
│   ├── point_cloud/
│   ├── precheck/
│   └── … (2 more entries)
└── third_party/
    └── upstream/
```
