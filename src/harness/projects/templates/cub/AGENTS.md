# Description of work on the classification of reference items

## Purpose

Helping assistants maintain CUB-200 classification items by physical access to enable code, inspection and results to demonstrate ResearchHarness project protocols together.

## Scope

Applys to the development and use of this template. First selects the maintenance mode and then finds the actual entry from the project README.

<!-- researchharness:search -->
## Locate projects and files

Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.
<!-- /researchharness:search -->

<!-- researchharness:mode -->
## Choose the maintenance mode

### Purpose and main functions

Use the project setting to select its maintenance guide and structure checker.

### Scope

Use this section for project maintenance, checking the online connection, or running an offline structure check.

Start by reading `.researchharness/mode.toml`. Its `enabled` setting selects this project's maintenance mode. Follow the user's choice and obtain authorization before changing it.

- **`enabled = false` selects offline maintenance.** Use the project's [offline operations guide](.researchharness/offline/operations.md). It explains how to plan, carry out, and finish maintenance using the project's files, commands, tests, and data.
- **`enabled = true` selects online maintenance.** Run `python -IS .researchharness/maintain.py status` first. When it prints `online`, read the central guide at the reported path. Follow that guide to the operations manual, shared skills, and central checks in the ResearchHarness repository. If the status command fails, report the cause and pause work that requires central maintenance until the user restores the connection or selects offline mode.
- **A missing or invalid setting blocks maintenance.** Report the problem and continue once the setting has been corrected or the user has chosen a mode.

When a structure check is authorized, run `python -IS .researchharness/maintain.py check` from the project root. The command runs the checker for the selected mode. Follow the project README for installation, training, prechecks, and reading results.
<!-- /researchharness:mode -->

## CUB project modus operandi

The data sets, models and tasks are selected from their respective `plugins.py` and `conf/config.yaml`. For each experiment, one or three words describing the purpose of the study are given as `subname`. Training, pre-testing and performance are compared to the `experiment/` at the root of the project. Validate with README ' s bounded formulation and read sub-lists and products with `inspect`.

The code, configuration and description are synchronized with the actual functions.
