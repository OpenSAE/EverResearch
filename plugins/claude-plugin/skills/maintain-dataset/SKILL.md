---
name: maintain-dataset
description: Add, update, or remove a research dataset. Use for dataset registration, loaders, preprocessing, splits, dataset choices, and verifying that a task reads the intended samples.
---

## Runtime compatibility

The repository skills are synchronized with EverResearch source. This distribution's launcher uses the published EverResearch 0.3.1 wheel. For source workflows that require the `.everresearch/` setup or a source-only command, use the CLI from the corresponding [EverResearch source checkout](https://github.com/OpenSAE/EverResearch/commit/9b036cb2109788a8545724a03c313502d255d187). Use the project's existing maintenance entry point when working with the published runtime.

# Maintain research datasets

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

Keep dataset sources, labels, splits, presets, and caches consistent with what tasks read through the project's `datasets/` components.

## Scope of application

Use this skill to add a dataset, source, or preset, change how a dataset is read or prepared, or remove dataset support. Identify the selected dataset, the tasks that use it, and the intended change. Start at the project's documented entry point and trace a representative sample from task selection back to its source and preparation.

For removals, check all users of the dataset or preset and verify the remaining selections. Preserve original inputs, shared caches, and historical results according to the project's requirements.

The [dataset procedures](references/procedures.md) explain file ownership, changes, and [acceptance with authentic data](references/procedures.md#accept-every-supported-dataset).

## Check project maintenance before editing

Before applying EverResearch rules to project edits, check the project's maintenance status with
`rh projects project status <project-root>`. If no mode has been selected, follow the repository's own rules. When the user
asks to use EverResearch on that project, hand off to [maintain-project](../maintain-project/SKILL.md)
for authorized setup before applying these rules. Read-only inspection and planning can proceed
before setup.

With `managed`, use
the reported guide and follow the authorized request. If the connection is unavailable or its
status cannot be verified, explain the gap and resolve it before applying EverResearch rules.


## Place preprocessed inputs under assets

Keep downloaded or original datasets under the workspace data root. Store project-produced inputs that are prepared for later use under `assets/prepared_data/<input-purpose>/files/`. This includes split manifests, processed feature stores, derived labels, and reusable preprocessing caches. Keep preparation code under `datasets/`. Put provenance in the asset's README or manifest, including the source, selection or split, effective preparation settings, and the names and identities of the generated files.

Follow the real producer and readers, including training, evaluation, comparison, and figure entry points. A prepared input shared by those consumers belongs to the named asset even when the first copy was produced by a training command. Give materially different source selections or partitions distinct descriptive names. Preserve the recorded input identity of past experiments while updating current defaults, producers, and readers to the revised location. Compare actual membership or file digests before and after the move. Keep disposable intermediate files with the temporary operation that creates them.

## Samples, labels, partitions or caches do not match configuration

Take a small batch of samples actually taken by the official mission and return the source, version, label, division and cache key for registration by sample status. Fix the preparation or logic of deviations. Rebuild the affected and renewable cache as agreed by the project and preserve the original input.

## Validation criteria

- Checks whether the sample identity, number, label meaning, sequence or shape, and whether the same data contract is followed in the case of a cache.
- If you are in a position to do so, you will be able to use the project’s comparative unit to verify the segregation, such as the object-level task of the study, by the identity of the object, and not just by line.

## Document Sync & Delivery

Synchronize data set entries, affected configurations and mission statements, and record how the source, sample, division or reading has changed. Deliver to humans the normal selection, actual sample evidence and impact on the comparability of existing tasks and experiments. `maintain-conf` Collaboration.

## Item-by-line

The data set is organized in terms of data sources and sample meanings. The named subset of the project definition is placed under the corresponding data set, indicating the selection, inclusion, labeling or division of differences and selection methods. The compatible preset for the same subset is written in the same entry. The text describes the source, sample unit, field and label, division and sample or preprocessing, selected tasks, output and limits. The different presets maintain the actual differences. The background is explained in the original paper or official description to determine the local behaviour by reading and formulating the project.

The text of the data set page presents the input, label, division and selection conditions, and a summary of how it supports the current selection is quoted in the data description. For example, indicate which queue the description of the supply classification applies.
