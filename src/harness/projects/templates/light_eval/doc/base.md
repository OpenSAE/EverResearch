# Runtime and entry points

## Purpose and main functions

`base/evaluation/` contains the console command dispatcher, Python Pipeline, shared runtime utilities, and result readers. Packaging maps source directories to the existing `lighteval` Python package.

## Scope

Use this page when following a user command to its backend, task selection, or saved result. The CLI dispatcher in `base/evaluation/__main__.py` registers backend and task commands. The commands under `base/evaluation/commands/` continue to be importable as `lighteval.main_*`.

The Pipeline resolves task IDs through the registry, asks each task for its evaluation requests, runs the sample precheck, and selects a model adapter. The result tracker reads study names from `conf/config.yaml` and saves effective settings, scores, and any sample details. Inspect AI runs through its native evaluator and log format.

The architecture guide follows both evaluation routes and identifies where to implement a change. [Project structure](code/evaluation/source/development/project-structure.mdx)
