# Description of work on the classification of reference items

## Purpose

Helping assistants maintain CUB-200 classification items by actual entry point to enable code, inspection and results to demonstrate ResearchHarness project protocols together.

## Scope

For the development and use of this template, search the portal from README.md and select the inspection and review mode by doc/code/development/engineering.md. When maintaining within the ResearchHarness source code, use the project protocol specified by the superior projects/PROTOCOL.md.

## Working methods

The data reading, modelling, classification tasks and operation support are grouped into corresponding modules. The new functionality is synchronized with the configuration, normal access, affected testing and reading of the results. The location of the corresponding directory, parameters, experiments, knowledge, environment and source structure is checked from doc/README.md. The code change updates the affected entries at the same time.

A programme to influence the disaggregation of data, indicators, numerical semantics, public access or calculator inputs, with practical examples and back and forth results. doc/code/development/engineering.md or specific responsibility modules, and where other projects are required, propose a central agreement or corresponding improvement of shared capacity.

## Shared skills

From this project. `.agents/skills/` Access to corresponding skills.`maintain-dataset`,`maintain-model` and `maintain-task` For adding, modifying and removing components,`maintain-conf` To add, delete or change parameters or meanings and default values,`maintain-experiment` For the selection of single parameters and for the execution, tracking, recovery, debugging and recording of experiments.`maintain-optional` External documents for independent maintenance of scripts, testing, documentation and inclusion of items.`maintain-base` Used to maintain basic coordination between components.`maintain-code` Used to review, repair and repeat codes by real scene.`maintain-skill` To assess the practical effects of the skills used in measuring and maintaining.`maintain-knowledge` For organizing and preserving knowledge.`extract-structure` Source structure for project extraction.

The choice of data sets, models and tasks from each other `plugins.py` with `conf/config.yaml` Find. Provides one or three words for each experiment. `subname`,Describes the experimental use or object of the experiment, the effective configuration is saved with a single operation. `experiment/`.Experiment press README Use of offline formulation in middle `python -m cub_template run`,Use it. `benchmark` It's a comparison. Use it. `inspect` Read the current operating list and product. The current training produces the final model weight. Follow-up runs determine the missing step from the operation log and verify whether the task supports restoration of integrity before continuing training.

_Other Organiser ResearchHarness When a source tree is used, the shared skills link is located directly in the centre. Skips when copying to an independent workspace `.agents/skills/`,Registered as a general item `rh projects apply <project ID>` Generate skills links in the workspace.
