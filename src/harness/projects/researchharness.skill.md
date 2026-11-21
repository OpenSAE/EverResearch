---
name: researchharness
description: Use of shared maintenance skills, in-house data and information from current projects Python Tie, and saved structural results.
---

# Project maintained with ResearchHarness

## Purpose

(b) To identify the shared skills, in-house resources and reversible structural results from the current project and to provide feedback on real project experience to the corresponding maintenance statement.

## Scope

The project README and its own dependencies, configurations and commands provide an independent installation and operation mode. ResearchHarness binds and starts the command to hand over its own resources to the same set of project portals as required.

- Determines the central directory and the project identifier from the central access paragraph of the project. The central relative path starts with the root of the project. Use the `rh projects --harness-root <harness-root> status <project-id>` query for the selected ResearchHarness. User requests to use `apply` for synchronisation, or `set --skills on` or `set --skills off` for changing the switch.
- In the selected ResearchHarness, `src/project/<project-id>/resources.json` saves the machine's data directory and Python. Use `rh projects resources <project-id>` query to update with `rh projects bind <project-id>`. Set to replace the unlocked atom and start the project and rely on installation to use the same binding.
- Under the same item directory `structure/<Results marker>/` Save `index.html` and `artifact.json`,Save after submission for review `decision.json`.Use it. `rh projects structure list <project ID>` View results, use `show` Check pages and review according to results markers. Project code review, formal plan and collaborative authorization along project lines GitHub Process.
- Project experiences record physical entry points, observed problems, outcomes and replicable practices. Human thought that deserves long-term preservation follows the `maintain-knowledge` entry process.

## Selecting skills for collation and maintenance

- **Access to an unknown project, inspection or maintenance of the whole project, using `maintain-project`.** Tracks the first-level catalogue and cross-component process from the actual order, defaults into the specific maintenance of the applicable parts and then checks the overall behaviour and delivery from the normal entrance.
- **Direct use of tailor-made skills for individual maintenance.** Datasets, models and missions are used separately `maintain-dataset`,`maintain-model` and `maintain-task`.Command distribution, cross-component access and shared operational capability use `maintain-base`.Use new, removed, semantic or default changes in public parameters `maintain-conf`.Single formulation, operation, result reading, tracking, recovery and experimental report use `maintain-experiment`.Use of stand-alone scripts, tests, component documents and external files `maintain-optional`.
- Read the corresponding `SKILL.md` from the actual skills directory of the current project. The central `src/harness/projects/README.md` attachment lists the skills entry, project engineering file specifications and in-house operations. The project using the engineering protocol goes from its own README to `doc/` to synchronize actual realization, parameters, entrances and products during maintenance and review.
- The existing entrance and the one-time work that cannot be performed at the official location is `maintain-tmp`. Depending on the installation using the central `rh projects install`, data preprocessing and reusable caches are attributed to the corresponding data root, and the Hugging Face download position is set at `huggingface-maintain`.
