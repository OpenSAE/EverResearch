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

- **Original project** [DINOv2](https://github.com/facebookresearch/dinov2)
- **Source revision** [`7764ea0f912e`](https://github.com/facebookresearch/dinov2/tree/7764ea0f912e53c92e82eb78a2a1631e92725fc8)
- **Paper** [DINOv2: Learning Robust Visual Features without Supervision](https://openreview.net/forum?id=a68SUt6zFt) · [TMLR 2024 Featured Certification](https://groups.google.com/g/tmlr-announce-weekly/c/zer0R3aCGrk)
- **Authors** Maxime Oquab, Timothée Darcet, Théo Moutakanni, Huy V. Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez, Daniel Haziza, Francisco Massa, Alaaeldin El-Nouby, Mido Assran, Nicolas Ballas, Wojciech Galuba, Russell Howes, Po-Yao Huang, Shang-Wen Li, Ishan Misra, Michael Rabbat, Vasu Sharma, Gabriel Synnaeve, Hu Xu, Hervé Jégou, Julien Mairal, Patrick Labatut, Armand Joulin, Piotr Bojanowski
- **Original source archive** [`dinov2.zip`](third_party/upstream/dinov2.zip)
- **Archive SHA-256** `04276715cddb29d45d05bff3a6fc132224dc27749b279ac98ad2ce4620e20d48`

### Before organization

```text
dinov2/
├── .github/
│   └── workflows/
├── dinov2/
│   ├── configs/
│   ├── data/
│   ├── distributed/
│   ├── eval/
│   ├── fsdp/
│   ├── hub/
│   ├── layers/
│   ├── logging/
│   ├── loss/
│   ├── models/
│   ├── run/
│   ├── thirdparty/
│   ├── train/
│   ├── utils/
│   └── … (1 more entries)
├── docs/
│   ├── Cell-DINO.png
│   ├── ChannelAdaptiveDINO.png
│   ├── README_CELL_DINO.md
│   └── README_CHANNEL_ADAPTIVE_DINO.md
├── notebooks/
│   ├── cell_dino/
│   ├── depth_estimation.ipynb
│   ├── dinotxt.ipynb
│   └── semantic_segmentation.ipynb
├── scripts/
│   ├── cell_dino/
│   └── lint.sh
├── .gitignore
├── CODE_OF_CONDUCT.md
├── conda-extras.yaml
├── conda.yaml
├── CONTRIBUTING.md
├── hubconf.py
├── LICENSE
├── LICENSE_CELL_DINO_CODE
├── LICENSE_CELL_DINO_MODELS
├── LICENSE_XRAY_DINO_MODEL
├── MODEL_CARD.md
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements-extras.txt
├── requirements.txt
├── setup.cfg
└── setup.py
```

### After organization

```text
dinov2/
├── .everresearch/
│   ├── offline/
│   ├── maintain.py
│   └── mode.toml
├── assets/
│   ├── figures/
│   └── licenses/
├── base/
│   ├── dino/
│   └── checkout.py
├── conf/
│   ├── tasks/
│   └── config.yaml
├── datasets/
│   ├── image_sources/
│   └── images/
├── doc/
│   ├── environment/
│   ├── knowledge/
│   ├── conf.md
│   ├── maintenance.md
│   └── README.md
├── models/
│   ├── hub/
│   ├── layers/
│   └── vision_transformer/
├── scripts/
│   ├── cell_dino/
│   ├── environment/
│   ├── notebooks/
│   ├── evaluate_image_classifiers.py
│   ├── evaluate_visual_heads.py
│   └── lint.sh
├── tasks/
│   ├── cell_classification/
│   ├── classification/
│   ├── depth_estimation/
│   ├── mask_segmentation/
│   ├── precheck/
│   ├── semantic_segmentation/
│   └── training/
├── third_party/
│   ├── clip/
│   ├── pytorch_hub/
│   ├── upstream/
│   └── README.md
├── .gitignore
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── requirements_dev.txt
├── requirements_extras.txt
├── setup.cfg
└── setup.py
```
