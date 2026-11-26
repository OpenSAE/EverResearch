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

- **Original project** [VGGT](https://github.com/facebookresearch/vggt)
- **Source revision** [a288dd0f14786c93483e45524328726ab7b1b4ce](https://github.com/facebookresearch/vggt/tree/a288dd0f14786c93483e45524328726ab7b1b4ce)
- **Paper** [VGGT: Visual Geometry Grounded Transformer](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html) · CVPR 2025 Oral, Best Paper
- **Authors** Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht, David Novotny
- **Original source archive** [vggt.zip](third_party/upstream/vggt.zip)
- **Archive SHA-256** `9e8aedd877b01628162d6cfd56cd4a1a93af813c0e86bd47132ecca47c29a913`

The archived revision matches the preserved model code and the VGGT-Omega announcement in the original README. The [maintenance record](doc/maintenance.md#recover-the-upstream-source-revision) explains how those files identify the source revision.

### Before organization

```text
vggt/
├── .gitattributes
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE.txt
├── README.md
├── demo_colmap.py
├── demo_gradio.py
├── demo_viser.py
├── docs/
│   └── package.md
├── examples/
│   ├── kitchen/
│   ├── llff_fern/
│   ├── llff_flower/
│   ├── room/
│   ├── single_cartoon/
│   └── … (2 more entries)
├── pyproject.toml
├── requirements.txt
├── requirements_demo.txt
├── training/
│   ├── README.md
│   ├── __init__.py
│   ├── config/
│   ├── data/
│   ├── launch.py
│   └── … (3 more entries)
├── vggt/
│   ├── dependency/
│   ├── heads/
│   ├── layers/
│   ├── models/
│   └── utils/
└── visual_util.py
```

### After organization

```text
vggt/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitattributes
├── .gitignore
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE.txt
├── README.md
├── assets/
│   └── examples/
├── base/
│   └── geometry_runtime/
├── conf/
│   ├── config.yaml
│   └── tasks/
├── datasets/
│   ├── common_objects_3d/
│   ├── multi_view/
│   └── virtual_kitti_2/
├── doc/
│   ├── README.md
│   ├── code/
│   ├── conf.md
│   ├── datasets.md
│   ├── environment/
│   └── … (5 more entries)
├── main.py
├── models/
│   └── geometry_transformer/
├── pyproject.toml
├── requirements.txt
├── requirements_demo.txt
├── scripts/
│   └── examples/
├── setup.py
├── tasks/
│   ├── fine_tune/
│   ├── precheck/
│   ├── reconstruction/
│   └── viewer/
├── tests/
│   ├── conftest.py
│   ├── test_entry_points.py
│   ├── test_result_paths.py
│   └── test_training_inputs.py
└── third_party/
    └── upstream/
```
