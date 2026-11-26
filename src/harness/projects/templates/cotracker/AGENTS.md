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

- **Original project** [CoTracker](https://github.com/facebookresearch/co-tracker)
- **Source revision** [`82e02e802975`](https://github.com/facebookresearch/co-tracker/tree/82e02e8029753ad4ef13cf06be7f4fc5facdda4d)
- **Paper** [CoTracker3: Simpler and Better Point Tracking by Pseudo-Labelling Real Videos](https://openaccess.thecvf.com/content/ICCV2025/html/Karaev_CoTracker3_Simpler_and_Better_Point_Tracking_by_Pseudo-Labelling_Real_Videos_ICCV_2025_paper.html) · [ICCV 2025 Highlight](https://iccv.thecvf.com/Conferences/2025/AcceptedPapers)
- **Authors** Nikita Karaev, Iurii Makarov, Jianyuan Wang, Natalia Neverova, Andrea Vedaldi, Christian Rupprecht
- **Original source archive** [`cotracker.zip`](third_party/upstream/cotracker.zip)
- **Archive SHA-256** `2706dfa5e6b800d56aee87b952f93c9855da0fa59c3cd06ef8ac9c03b3b083f9`

### Before organization

```text
co-tracker/
├── assets/
│   ├── apple.mp4
│   ├── apple_mask.png
│   ├── bmx-bumps.gif
│   └── teaser.png
├── cotracker/
│   ├── datasets/
│   ├── evaluation/
│   ├── models/
│   ├── utils/
│   ├── __init__.py
│   ├── predictor.py
│   └── version.py
├── docs/
│   ├── source/
│   └── Makefile
├── gradio_demo/
│   ├── videos/
│   ├── app.py
│   └── requirements.txt
├── notebooks/
│   └── demo.ipynb
├── tests/
│   └── test_bilinear_sample.py
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── demo.py
├── hubconf.py
├── launch_training_kubric_offline.sh
├── launch_training_kubric_online.sh
├── launch_training_scaling_offline.sh
├── launch_training_scaling_online.sh
├── LICENSE.md
├── online_demo.py
├── README.md
├── setup.py
├── train_on_kubric.py
└── train_on_real_data.py
```

### After organization

```text
cotracker/
├── .everresearch/
│   ├── offline/
│   ├── maintain.py
│   └── mode.toml
├── assets/
│   ├── images/
│   ├── videos/
│   └── README.md
├── base/
│   └── tracking/
├── conf/
│   ├── tasks/
│   └── config.yaml
├── datasets/
│   └── video_tracking/
├── doc/
│   ├── code/
│   ├── environment/
│   ├── knowledge/
│   ├── base.md
│   ├── conf.md
│   ├── datasets.md
│   ├── experiment.md
│   ├── maintenance.md
│   ├── models.md
│   ├── README.md
│   ├── scripts.md
│   ├── tasks.md
│   └── tests.md
├── models/
│   ├── network/
│   └── tracking/
├── scripts/
│   ├── examples/
│   └── training/
├── tasks/
│   ├── evaluation/
│   ├── precheck/
│   ├── tracking/
│   └── training/
├── tests/
│   └── test_bilinear_sample.py
├── third_party/
│   └── upstream/
├── .gitignore
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE.md
├── main.py
├── pyproject.toml
├── README.md
├── requirements_gradio.txt
└── setup.py
```
