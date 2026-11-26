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

## Increase

1. Read the scene from downstream to determine the meaning of input, mission steps, indicators, deliverables and partial completion.
2. Reuse actual training, evaluation and record-keeping support when the catalogue is responsible for public interfaces and calculations. `tasks/` Down `precheck`,Allows the public entry point to run a precheck automatically in the current combination before each count. Using a very small sample, the formal computation, product path, writing format and reading, the precheck is followed by a formal calculation.
3. Synchronize public commands, project descriptions and required result readers.
4. If you are allowed to do so, enter a representative input and read the results from the normal entrance, confirming that the intended product can be obtained downstream.

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

## Points for reference items

The CUB template `tasks/classification/task.py` accepts and validates the official combination, `tasks/classification/operation.py` to achieve the classification step. `tasks/plugins.py` Register classification and precheck, `conf/config.yaml` sets the default parameters for the task. When you change the classification indicator, you track the results field in the report and the list and position it from `inspect` to the corresponding output.
