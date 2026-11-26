# WhisperResearch maintenance

## Purpose and main function

Find the instructions used to maintain and verify the WhisperResearch checkout.

## Scope of application

Use this document when reviewing code, moving project files, or checking an EverResearch connection. Install and run Whisper as described in the project [README](README.md). The [project guide](doc/README.md) maps the command and Python API to the code that implements them.

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

- **Original project** [Whisper](https://github.com/openai/whisper)
- **Source revision** [`86098128c0b4`](https://github.com/openai/whisper/tree/86098128c0b4f24f0e2aa2994de830614b474227)
- **Paper** [Robust Speech Recognition via Large-Scale Weak Supervision](https://proceedings.mlr.press/v202/radford23a.html) · ICML 2023 Poster
- **Authors** Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine Mcleavey, Ilya Sutskever
- **Original source archive** [`whisper.zip`](third_party/upstream/whisper.zip)
- **Archive SHA-256** `1e30f6543d697a0a3e5ab6f2d0564ab006e636f6e200140b9e80c6d168c47b99`

### Before organization

```text
whisper/
├── .github/
│   ├── workflows/
│   └── dependabot.yml
├── data/
│   ├── meanwhile.json
│   └── README.md
├── notebooks/
│   ├── LibriSpeech.ipynb
│   └── Multilingual_ASR.ipynb
├── tests/
│   ├── conftest.py
│   ├── jfk.flac
│   ├── test_audio.py
│   ├── test_normalizer.py
│   ├── test_timing.py
│   ├── test_tokenizer.py
│   └── test_transcribe.py
├── whisper/
│   ├── assets/
│   ├── normalizers/
│   ├── __init__.py
│   ├── __main__.py
│   ├── audio.py
│   ├── decoding.py
│   ├── model.py
│   ├── timing.py
│   ├── tokenizer.py
│   ├── transcribe.py
│   ├── triton_ops.py
│   ├── utils.py
│   └── version.py
├── .flake8
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── approach.png
├── CHANGELOG.md
├── language-breakdown.svg
├── LICENSE
├── MANIFEST.in
├── model-card.md
├── pyproject.toml
├── README.md
└── requirements.txt
```

### After organization

```text
whisper/
├── .everresearch/
│   ├── offline/
│   ├── maintain.py
│   └── mode.toml
├── assets/
│   ├── documentation/
│   ├── model_inputs/
│   └── prepared_data/
├── base/
│   └── whisper/
├── conf/
│   └── config.json
├── datasets/
│   └── audio/
├── doc/
│   ├── environment/
│   ├── experiment/
│   ├── knowledge/
│   ├── conf.md
│   ├── data.md
│   ├── maintenance.md
│   └── README.md
├── models/
│   └── whisper/
├── scripts/
│   ├── examples/
│   └── run_speech_workload.py
├── tasks/
│   ├── evaluation/
│   ├── precheck/
│   └── speech/
├── tests/
│   ├── fixtures/
│   ├── conftest.py
│   ├── test_audio.py
│   ├── test_normalizer.py
│   ├── test_timing.py
│   ├── test_tokenizer.py
│   └── test_transcribe.py
├── third_party/
│   └── upstream/
├── .flake8
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```
