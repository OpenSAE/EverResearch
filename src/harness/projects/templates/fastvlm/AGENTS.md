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

- **Original project** [FastVLM](https://github.com/apple-aiml-research/ml-fastvlm)
- **Source revision** [6f7b13179bbc81e6aa7d921bc7c6335c43904778](https://github.com/apple-aiml-research/ml-fastvlm/tree/6f7b13179bbc81e6aa7d921bc7c6335c43904778)
- **Paper** [FastVLM: Efficient Vision Encoding for Vision Language Models](https://openaccess.thecvf.com/content/CVPR2025/papers/Vasu_FastVLM_Efficient_Vision_Encoding_for_Vision_Language_Models_CVPR_2025_paper.pdf) · CVPR 2025 Poster
- **Authors** Pavan Kumar Anasosalu Vasu, Fartash Faghri, Chun-Liang Li, Cem Koc, Nate True, Albert Antony, Gokul Santhanam, James Gabriel, Peter Grasch, Oncel Tuzel, Hadi Pouransari
- **Original source archive** [fastvlm.zip](third_party/upstream/fastvlm.zip)
- **Archive SHA-256** `12a1c2d5180faf624321b0fcea310e9e0e2b19e983a7d34635c00142364f83d1`

The [earlier maintenance record](doc/code/previous_maintenance.md) identifies the starting revision.

### Before organization

```text
ml-fastvlm/
├── .gitignore
├── ACKNOWLEDGEMENTS
├── LICENSE
├── LICENSE_MODEL
├── README.md
├── app/
│   ├── Configuration/
│   ├── FastVLM App/
│   ├── FastVLM.xcodeproj/
│   ├── FastVLM/
│   ├── README.md
│   └── … (2 more entries)
├── docs/
│   ├── acc_vs_latency_qwen-2.png
│   ├── fastvlm-counting.gif
│   ├── fastvlm-emoji.gif
│   ├── fastvlm-flexible_prompts.png
│   └── fastvlm-handwriting.gif
├── get_models.sh
├── llava/
│   ├── __init__.py
│   ├── constants.py
│   ├── conversation.py
│   ├── mm_utils.py
│   ├── model/
│   └── … (3 more entries)
├── model_export/
│   ├── README.md
│   ├── export_vision_encoder.py
│   └── fastvlm_mlx-vlm.patch
├── predict.py
└── pyproject.toml
```

### After organization

```text
fastvlm/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .github/
│   └── workflows/
├── .gitignore
├── AGENTS.md
├── LICENSE
├── README.md
├── assets/
│   ├── documentation/
│   ├── examples/
│   ├── integration/
│   └── licensing/
├── base/
│   ├── fast_vlm/
│   └── language_vision/
├── conf/
│   ├── config.json
│   └── models/
├── datasets/
│   ├── __init__.py
│   ├── supervised/
│   └── user_image/
├── doc/
│   ├── README.md
│   ├── code/
│   ├── conf.md
│   ├── data.md
│   ├── datasets.md
│   └── … (5 more entries)
├── main.py
├── models/
│   ├── __init__.py
│   ├── fast_vision/
│   └── model/
├── pyproject.toml
├── scripts/
│   └── models/
├── tasks/
│   ├── __init__.py
│   ├── image_prompt/
│   ├── precheck/
│   ├── serve/
│   └── train/
├── tests/
│   ├── conftest.py
│   ├── test_inference.py
│   └── test_model_export.py
└── third_party/
    ├── README.md
    ├── apple_demo/
    └── upstream/
```
