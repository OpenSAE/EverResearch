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

- **Original project** [SAM 2](https://github.com/facebookresearch/sam2)
- **Source revision** [2b90b9f5ceec907a1c18123530e92e794ad901a4](https://github.com/facebookresearch/sam2/tree/2b90b9f5ceec907a1c18123530e92e794ad901a4)
- **Paper** [SAM 2: Segment Anything in Images and Videos](https://proceedings.iclr.cc/paper_files/paper/2025/hash/45c1f6a8cbf2da59ebf2c802b4f742cd-Abstract-Conference.html) · ICLR 2025 Oral
- **Authors** Nikhila Ravi, Valentin Gabeur, Yuan-Ting Hu, Ronghang Hu, Chaitanya Ryali, Tengyu Ma, Haitham Khedr, Roman Rädle, Chloe Rolland, Laura Gustafson, Eric Mintun, Junting Pan, Kalyan Vasudev Alwala, Nicolas Carion, Chao-Yuan Wu, Ross Girshick, Piotr Dollár, Christoph Feichtenhofer
- **Original source archive** [sam2.zip](third_party/upstream/sam2.zip)
- **Archive SHA-256** `fe93082a71a885a427894b1eab76341768781b6b58a298a0717e03862097d137`

### Before organization

```text
sam2/
├── .clang-format
├── .github/
│   └── workflows/
├── .gitignore
├── .watchmanconfig
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── INSTALL.md
├── LICENSE
├── LICENSE_cctorch
├── MANIFEST.in
├── README.md
├── RELEASE_NOTES.md
├── assets/
│   ├── model_diagram.png
│   └── sa_v_dataset.jpg
├── backend.Dockerfile
├── checkpoints/
│   └── download_ckpts.sh
├── demo/
│   ├── .gitignore
│   ├── README.md
│   ├── backend/
│   ├── data/
│   └── frontend/
├── docker-compose.yaml
├── notebooks/
│   ├── automatic_mask_generator_example.ipynb
│   ├── image_predictor_example.ipynb
│   ├── images/
│   ├── video_predictor_example.ipynb
│   └── videos/
├── pyproject.toml
├── sam2/
│   ├── __init__.py
│   ├── automatic_mask_generator.py
│   ├── benchmark.py
│   ├── build_sam.py
│   ├── configs/
│   └── … (10 more entries)
├── sav_dataset/
│   ├── LICENSE
│   ├── LICENSE_DAVIS
│   ├── LICENSE_VOS_BENCHMARK
│   ├── README.md
│   ├── example/
│   └── … (4 more entries)
├── setup.py
├── tools/
│   ├── README.md
│   └── vos_inference.py
└── training/
    ├── README.md
    ├── __init__.py
    ├── assets/
    ├── dataset/
    ├── loss_fns.py
    └── … (6 more entries)
```

### After organization

```text
sam2/
├── .clang-format
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .github/
│   └── workflows/
├── .gitignore
├── .watchmanconfig
├── AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── assets/
│   ├── examples/
│   ├── figures/
│   └── native_extension/
├── base/
│   ├── segment_anything/
│   └── training/
├── conf/
│   ├── config.yaml
│   ├── models/
│   └── tasks/
├── datasets/
│   ├── annotations/
│   ├── notebook_images/
│   └── video_objects/
├── doc/
│   ├── README.md
│   ├── base.md
│   ├── code/
│   ├── conf.md
│   ├── datasets.md
│   └── … (5 more entries)
├── main.py
├── models/
│   └── segment_anything/
├── pyproject.toml
├── scripts/
│   ├── dataset/
│   ├── examples/
│   ├── training/
│   └── video/
├── setup.py
├── tasks/
│   ├── benchmarking/
│   ├── evaluation/
│   ├── fine_tuning/
│   ├── image_segmentation/
│   ├── precheck/
│   └── … (1 more entries)
├── tests/
│   ├── conftest.py
│   ├── test_image_inference.py
│   ├── test_training_config.py
│   └── test_vos_inference.py
└── third_party/
    ├── meta_web_demo/
    └── upstream/
```
