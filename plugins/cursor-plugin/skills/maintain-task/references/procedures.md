# Task Operating Scheme

## Purpose

Description of the process by which tasks go from configuration and distribution to computation and then to results users, as well as the documents responsible for the various types of changes.

## Scope

Adds, modifies or removes items for research tasks, workflows and task outputs.

## Attribution of files

| Location | Responsible content |
| --- | --- |
| `tasks/<task>/task.py` | Open access, parameters and data model combination check, return mission results |
| `tasks/<task>/operation.py`、`evaluation.py` | Methodological calculations, training and mission-specific evaluations. Assessment documents are available when independent assessments are required |
| `tasks/<task>/<subtask>/` | Steps or methods that can be independently called under the same research objective. The scientific logic of shared sub-missions is maintained by the named module of the mission. |
| `tasks/plugins.py` or `tasks/workflows.py` | The task or workflow public identification and distribution. The main command resolves the parameters and calls the official realization. |
| `conf/config.yaml` and corresponding experiments catalogue | Mission parameters, workload, selected data models and operating conditions |
| `tasks/precheck/` | Selection of independent precheck, precheck of official assignments, timing and performance comparisons |
| Project Public Operating Layer and Results Reader | Registers the status of operations, the environment and the location of the product. Consumers use the list to locate and explain the results. |

When determining the attribution of the common code, look at whether it handles a sample, model, scientific mission or running process. The label is read with data, model construction and weighting with models, and the general check point status and file reading and writing with the operational layer. The results table with task-specific fields follows the task.

## Add a task

1. Trace a similar task from the normal command to the registry, configuration, automatic precheck, worker, output writer, and reader. Search for that task name in those direct callers and relevant tests to find any separate allowlists or task-specific behavior.
2. Reuse the registry to discover tasks wherever callers need the same population. Keep task-specific preparation and evidence with the task or precheck branch that owns them. Keep assertions for actual behavior and count the registered tasks as a set when testing generic coverage.
3. Validate the installed command from outside the checkout. Add the new task and its configuration after editable installation. Exercise discovery and the automatic worker with the same installation. Verify the wheel separately when the task ships. Use the project's documented development dependencies for contribution checks.
4. Through the normal command, exercise a bounded automatic precheck followed by the task and its result reader. Inspect the actual precheck receipt or worker result for the new task. A configuration preview proves discovery, and the precheck receipt proves that the new registration passed the real gate. Exercise a rejected input when the gate changes and confirm it stops before formal execution.

## Modify

1. Checks for real calls, parameter defaults, prechecks, product formats, and historical results. Clear changes are made for task calculations, data model combinations, run-formulations, or result readings.
2. Move the changes to the responsible file. Algorithm changes enter the calculation module, interface check access to the task portal, common running records change to the public operating layer, and report readers who interpret the results synchronize with the output.
3. When it comes to indicators, mission semantics, public commands, or results formats, list the means of reading the affected users and historical materials.
4. The selection of the same representative input to check for old and new behaviour when granted, and the verification of normal, blocked or partial completion is understood by the actual result reader.

## Remove

1. Determines the range of subtasks, modes, parameters, products, or the whole task. Finds the official registration, preset, default values, logs and reports for reading, periodic start-up and exclusive testing.
2. The common load, assessment or reporting logic is subordinated to the remaining actual use.
3. Cancels the selected mode or output. Synchronizes the removal of public commands, realization, configuration, exclusive inspection and activity descriptions on unmounting. Existing operations and materials are processed according to specific authorization.
4. Checks the removal of the selected entry and the retention of the workflow.

## Run a bounded precheck for every task

- Use the same effective configuration and production precheck from both a precheck-only
  command and the official task launch. A normal launch calls it automatically before formal
  computation. Resolve each supported selection and reject incompatible selections with a
  specific reason. Verify a successful and blocked launch for each materially distinct gate.
- Through that entry, read a small real sample through the selected loader, construct the
  actual model and load the selected weights, perform the smallest meaningful computation,
  and write and reopen a minimal result through the normal interfaces. Choose the real
  operation by task. For training, include backward and an optimizer step when those paths
  apply. For evaluation, exercise the metric readback. Use a temporary output location and
  isolate model, optimizer, and random state so the precheck preserves the formal run state.
- During first-time setup, follow the [short-run guidance](../../maintain-project/references/coordination.md#keep-setup-runs-short)
  for task checks and smoke runs. Bound time, samples,
  steps or frames, and output size. Measure startup
  and a small representative compute interval separately, report the workload unit and
  environment, and stop with a recorded gap when required work exceeds the budget. Reuse
  verified component evidence for unchanged selections. Run additional cases for different
  data contracts, weight formats, execution branches, or output formats.
- Record the effective selection, checks reached, measured times and counts, output readback,
  and blocker if any. A precheck-only result ends before formal computation. When testing the
  automatic gate with a bounded formal smoke run, keep a succeeded and a rejected record
  and use the central paired precheck checker where its manifest format applies. A path
  inventory or argument preview covers configuration resolution.

## Points for reference items

The CUB template `tasks/classification/task.py` accepts and validates the official combination, `tasks/classification/operation.py` to achieve the classification step. `tasks/plugins.py` Register classification and precheck, `conf/config.yaml` sets the default parameters for the task. When you change the classification indicator, you track the results field in the report and the list and position it from `inspect` to the corresponding output.
