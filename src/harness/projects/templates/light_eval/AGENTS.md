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

- **Original project** [LightEval](https://github.com/huggingface/lighteval)
- **Source revision** [`b97a6533bec2`](https://github.com/huggingface/lighteval/tree/b97a6533bec22c4184b88526366fdf5d73d502c9)
- **Paper** No dedicated paper
- **Authors** Nathan Habib, Clémentine Fourrier, Hynek Kydlíček, Thomas Wolf, Lewis Tunstall
- **Original source archive** [light_eval.zip](third_party/upstream/light_eval.zip)
- **Archive SHA-256** `eefb8094007f9a81fe286f2569850e8027dee51b5d5d19dae22806fd5b60e70a`

### Before organization

```text
lighteval/
├── .gitattributes
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── dependabot.yml
│   ├── release.yml
│   └── workflows/
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── assets/
│   └── lighteval-doc.svg
├── docs/
│   └── source/
├── examples/
│   ├── custom_models/
│   ├── custom_tasks_templates/
│   ├── custom_tasks_tests.py
│   ├── model_configs/
│   ├── nanotron/
│   ├── tasks/
│   └── test_tasks.txt
├── pyproject.toml
├── setup.py
├── src/
│   └── lighteval/
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── fixtures.py
    ├── reference_details/
    ├── reference_scores/
    ├── slow_tests/
    ├── test_dependencies.py
    ├── test_unit_base_metrics.py
    ├── test_unit_harness_metrics.py
    ├── unit/
    └── utils.py
```

### After organization

```text
light_eval/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitattributes
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── dependabot.yml
│   ├── release.yml
│   └── workflows/
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── LICENSE
├── Makefile
├── README.md
├── assets/
│   ├── branding/
│   ├── evaluation/
│   └── examples/
├── base/
│   └── evaluation/
├── conf/
│   └── config.yaml
├── datasets/
│   ├── evaluation_batches/
│   └── huggingface_hub/
├── doc/
│   ├── README.md
│   ├── base.md
│   ├── code/
│   ├── conf.md
│   ├── datasets.md
│   ├── environment/
│   ├── experiment.md
│   ├── maintenance.md
│   ├── models.md
│   └── tasks.md
├── models/
│   └── adapters/
├── pyproject.toml
├── pytest.ini
├── scripts/
│   └── examples/
├── setup.py
├── tasks/
│   ├── benchmarks/
│   ├── chance_baseline/
│   ├── core_benchmarks/
│   ├── language_support/
│   ├── metrics/
│   ├── multilingual_benchmarks/
│   ├── precheck/
│   └── prompt_templates/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   ├── integration/
│   ├── product/
│   ├── test_dependencies.py
│   ├── test_unit_base_metrics.py
│   └── test_unit_harness_metrics.py
└── third_party/
    └── upstream/
        └── light_eval.zip
```
