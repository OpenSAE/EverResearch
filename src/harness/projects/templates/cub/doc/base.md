# Base Layer

## Purpose

Describes how the commands are configured, packaged and the results preserved.

## Scope

To maintain the command, operational coordination and outcome interface of the project `base/cub_template/`.

- [Command entrance](../base/cub_template/cli.py)Parsing Runs, Prechecks, Performance Comparisons and Results View.
- [Registration](../base/cub_template/registry.py)Select data, models and tasks from actual components.
- [Run Layer](../base/cub_template/runtime/runner.py)Preparing the environment, checking the mix, and carrying out tasks;[Record module](../base/cub_template/runtime/records.py)Save Configuration and List.
- Enter the resources required for the formulation, running-time coverage and selected components. Output the task result or cause-based operational status of the completed task, by `inspect` Query. Modify Coordinated Behaviour From [Normal access and return of results](../tests/test_workflow.py) Check, sync when parameters or results are involved [Configure](conf.md)(Check profile, default and overwhelming rules, searchable `training.batch_size` the default value and effect) and [Experimental report](experiment.md)(Use to compare results and limits based on real operations, check for random initialization and fine-tuning of respective conditions).
