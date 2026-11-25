# Maintain BirdStudy

## Purpose and main function

Keep this bird classification example runnable through its documented commands. It demonstrates how dataset, model, task, configuration, and experiment files fit together.

## Scope of application

Use these instructions when editing or running this example. Start with the README and follow the project's maintenance mode.

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
- **`enabled = true` selects online maintenance.** Run `python -IS .researchharness/maintain.py status` first. When it prints `online`, read the central guide at the reported path. Follow that guide to the operations manual, shared skills, and central checks in the EverResearch repository. If the status command fails, report the cause and pause work that requires central maintenance until the user restores the connection or selects offline mode.
- **A missing or invalid setting blocks maintenance.** Report the problem and continue once the setting has been corrected or the user has chosen a mode.

When a structure check is authorized, run `python -IS .researchharness/maintain.py check` from the project root. The command runs the checker for the selected mode. Follow the project README for installation, training, prechecks, and reading results.
<!-- /researchharness:mode -->

## Working on the example

Select the dataset, model, and task through the existing registries and configuration. Use a descriptive experiment name such as `offline_check`. Run the documented precheck or a small synthetic example for the affected behavior. Use the normal result reader to inspect the run record and artifacts.

Keep the README and component guides aligned with the commands people can run.
