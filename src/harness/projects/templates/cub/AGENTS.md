# Description of work on the classification of reference items

## Purpose

Helping assistants maintain CUB-200 classification items by actual entry point to enable code, inspection and results to demonstrate ResearchHarness project protocols together.

## Scope

Applys to the development and use of this template by searching for portals from README.md and selecting the inspection and review mode by doc/code/development/engineering.md. When maintaining within the ResearchHarness source code, use the project protocol specified by the superior projects/README.md#project-execution.

## Working methods

The data reading, modelling, classification tasks and operation support are grouped into corresponding modules. The new functionality is synchronized with the configuration, normal access, affected testing and reading of the results. The location of the corresponding directory, parameters, experiments, knowledge, environment and source structure is checked from doc/README.md. The code change updates the affected entries at the same time.

A programme to influence the disaggregation of data, indicators, numerical semantics, public access or calculator inputs, with practical examples and back and forth results. doc/code/development/engineering.md or specific responsibility modules, and where other projects are required, propose a central agreement or corresponding improvement of shared capacity.

## Shared skills

Read the corresponding skills from `.agents/skills/` for this item. `maintain-dataset`, `maintain-model` and `maintain-task` for adding, modifying and removing components, `maintain-conf` for adding and deleting parameters or changing meanings and default values, `maintain-experiment` for selecting single parameters and implementing, tracking, restoring, debugging and recording experiments. `maintain-optional` for independent maintenance of scripts, testing, documentation and external documentation for inclusion in the project. `maintain-base` for maintaining basic coordination between components. `maintain-code` for reviewing, repairing and resurveying codes based on real scenes. `maintain-skill` for evaluating and maintaining the practical effects of skills. `maintain-knowledge` for organizing and preserving knowledge. `extract-structure` For project extract source structure.

The selection of data sets, models and tasks is found from `plugins.py` to `conf/config.yaml`. For each experiment, one to three words `subname` are given, describing the experimental use or object of exploration, and is configured to be stored with a single operation. Training, precheck and performance comparisons are included at `experiment/` of the root of the project. The experiment uses `python -m cub_template run` for offline formulations in README, and `benchmark` for performance comparison, and reads already operating lists and products from `inspect`. The current training is leading to the final model weighting. Follow-up runs determine from the running records what is missing and continue to train to verify whether the task supports restoration.

_Other Organiser ResearchHarness The shared skills link is located directly in the middle of the source tree. Skips when copying to an independent workspace `.agents/skills/`,Registered as a general item `rh projects apply <project ID>` Generate skills links in the workspace.
