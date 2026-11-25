---
name: maintain-model
description: Add, change, or remove a research model or variant. Use for model configuration, weights, initialization, model interfaces, and compatibility with a task.
---

# Maintain research models

## Run the EverResearch CLI

Use Python 3.11, 3.12, or 3.13 to run `scripts/rh.py` from the current skill,
followed by the arguments after `rh`. For example, pass `projects project check <project-path>` to check a
project. Use `${CLAUDE_SKILL_DIR}` in Claude Code or Cowork and the staged skill
directory in Claude web.

The launcher uses the packaged runtime when available. GitHub marketplace
installs download the pinned wheel once and verify its checksum before use.
The launcher creates a private environment and may fetch Python dependencies.
With no Python execution available, review the files you can
access and tell the user which automated checks you could not run.

For a separate terminal installation, the official PyPI package is
`ever-research` from OpenSAE. The PyPI project named `researchharness` is
maintained separately.

## Purpose and main function

Keep model construction, weight selection, and task-facing outputs consistent with the model selected through the project's public entry point.

## Scope of application

Use this skill to add a model family or variant, change its architecture, inputs or weights, or remove a preset, variant, or supported combination. Identify the selected model and trace the output used by the task back through construction and weight loading. Check direct model callers where the project exposes them.

The [model procedures](references/procedures.md) cover model families, historical weights, and how to verify additions, changes, and removals.

## Check project maintenance before editing

Before applying EverResearch rules to project edits, check the project root for
`.researchharness/mode.toml`. If it is missing, follow the repository's own rules. When the user
asks to use EverResearch on that project, hand off to [maintain-project](../maintain-project/SKILL.md)
for authorized setup before applying these rules. Read-only inspection and planning can proceed
before setup.

If the mode file is present, run `rh projects project status <project-root>`. With `managed`, use
the reported guide and follow the authorized request. If the connection is unavailable or its
status cannot be verified, explain the gap and resolve it before applying EverResearch rules.


## Variable, weight or task output does not match the selected model

Checks the model identification, physical construction parameters, version of weight, load results and output of task consumption along the official mission entry. The actual selection, construction or reading error is repaired. The Python that normally constructs the entry is used to load the name variant and the corresponding weight, to process a small input and check the output used by the task. Checks the cause of failure with clearly incompatible input. The model directory uses a central layout check. Report on the actual load, still available combination and the resulting impact.

## Validation criteria

- Searches for a physical compatibility combination. Checks if the source, tectonic parameters and weight rereading match, and identifies the entry from the mission fixed model rather than consuming model options.
- The selection range of models to be checked for results from the configuration or preservation in effect. This involves recording the data used in the selected model and the conditions required for subsequent independent comparisons when early stoppage, candidate model comparison or reprocessing is proposed.

## Document Sync & Delivery

Synchronizes model entries, affected configurations, and mission statements. Report on available models and weights, normal selection methods, actual output basis, and whether old weights or task combinations can be followed. `maintain-conf` Collaboration.

The changes are recorded in the project-by-project project file.

## Item-by-line

A description of the model family and series of organizations. The common construction and weight rules are placed in the upper tier, with each submodel that can be selected individually describing the differences and public entry point to the other members of the family. Write down the structure, use, input output, source and initialization of weights, describing and actual differences from other options in the series, applicable tasks and known limitations. The original model card describes the facts upstream, and project construction and re-analysis describes local behaviour.

The main text of the model page refers to the conditions, weights, and actual differences. The model or version it covers is summarized in other notes, e.g., an indication of which copyright weight is explained by a model card.
