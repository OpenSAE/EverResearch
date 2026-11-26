# Maintain BirdStudy

## Purpose and main function

Keep this bird classification example runnable through its documented commands. It demonstrates how dataset, model, task, configuration, and experiment files fit together.

## Scope of application

Use these instructions when editing or running this example. Start with the README and follow the project's maintenance mode.

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

## Working on the example

Select the dataset, model, and task through the existing registries and configuration. Use a descriptive experiment name such as `offline_check`. Run the documented precheck or a small synthetic example for the affected behavior. Use the normal result reader to inspect the run record and artifacts.

Keep the README and component guides aligned with the commands people can run.

## Original project and template layout

- **Original project** [BirdStudy](https://github.com/OpenSAE/EverResearch)
- **Source revision** [BirdStudy v0.3.1 example release](https://github.com/OpenSAE/EverResearch/releases/download/v0.3.1/ever-research-0.3.1-example.zip)
- **Paper** No dedicated paper
- **Authors** OpenSAE
- **Original source archive** [birdstudy.zip](third_party/upstream/birdstudy.zip)
- **Archive SHA-256** `58310178a18bb6c72bf1cc13ed078af41450da1a2e12c4ba96a2e141ef53ee4e`
- **Dataset paper** [The Caltech-UCSD Birds-200-2011 Dataset](https://authors.library.caltech.edu/records/cvm3y-5hh21) · Caltech Technical Report 2011
- **Dataset authors** Catherine Wah, Steve Branson, Peter Welinder, Pietro Perona, Serge Belongie

### Before organization

```text
BirdStudy/
├── .gitignore
├── .researchharness/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── AGENTS.md
├── README.md
├── base/
│   └── cub_template/
├── conf/
│   └── config.yaml
├── datasets/
│   ├── __init__.py
│   ├── cub200/
│   └── plugins.py
├── doc/
│   ├── README.md
│   ├── agents.md
│   ├── base.md
│   ├── code/
│   ├── conf.md
│   └── … (7 more entries)
├── experiment/
│   ├── cub200/
│   └── synthetic/
├── models/
│   ├── __init__.py
│   ├── build.py
│   ├── convolution/
│   ├── plugins.py
│   └── residual/
├── pyproject.toml
├── tasks/
│   ├── __init__.py
│   ├── classification/
│   ├── plugins.py
│   └── precheck/
└── tests/
    ├── test_boundaries.py
    └── test_workflow.py
```

### After organization

```text
BirdStudy/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitignore
├── AGENTS.md
├── README.md
├── base/
│   └── cub_template/
├── conf/
│   └── config.yaml
├── datasets/
│   ├── __init__.py
│   ├── cub200/
│   └── plugins.py
├── doc/
│   ├── README.md
│   ├── agents.md
│   ├── base.md
│   ├── code/
│   ├── conf.md
│   └── … (8 more entries)
├── experiment/
│   ├── cub200/
│   └── synthetic/
├── models/
│   ├── __init__.py
│   ├── build.py
│   ├── convolution/
│   ├── plugins.py
│   └── residual/
├── pyproject.toml
├── tasks/
│   ├── __init__.py
│   ├── classification/
│   ├── plugins.py
│   └── precheck/
├── tests/
│   ├── test_boundaries.py
│   └── test_workflow.py
└── third_party/
    └── upstream/
```
