---
name: maintain-experiment
description: Run, monitor, recover, or review a research experiment. Use for run recipes, effective configurations, execution records, and results produced by the experiment.
---

# Run and maintain research experiments

## Purpose and main function

Start, monitor, resume, or review a research experiment. Keep the effective configuration, run record, and outputs together.

## Scope of application

Use for a specific run, a group of runs, or their results. Read the project's instructions and use its documented commands within the user's authorization.

## Follow the run from configuration to result

1. Identify the selected data, model, task, configuration, and expected results. Use the project's defaults and existing recipes, then apply overrides through its public entry point. Use `maintain-conf` for changes to the available parameters or defaults.
2. Confirm the effective configuration and normal precheck before computation. Use `maintain-task` if the precheck, entry point, or rejection behavior needs repair.
3. Keep run-specific records and results under `experiment/`. Keep reusable preprocessing inputs in the named assets defined by `maintain-dataset`. Save the effective configuration, selected inputs, command, status and output locations with the run.
4. Read results through the project's normal reader. Use `rh projects experiment check <project-root>` for experiment records and `rh projects project check <project-root>` when the change also affects project layout. Confirm the result and report any checks still needed.

## Read details when needed

- [Run paths](references/run-paths.md) covers directory structure, meaningful names, and historical result paths. Read before creating, moving, or renaming run outputs.
- [Run verification](references/run-verification.md) covers tracking, recovery, profiling, and verification. Read for failures, performance comparisons, and result handoff.
- [Experiment procedures](references/procedures.md) explains configuration recovery, result reading, and the steps used to investigate common run problems.
