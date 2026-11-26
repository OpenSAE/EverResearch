# Verify, recover, and report experiments

## Purpose and main function

Verify, recover, and report experiments.

## Scope of application

Use for monitoring, recovery, performance diagnosis, failed checks, or result handoff.

## Prepare the formal run choices

For each public research task, select at least one priority supported dataset and model combination
using the project's documented defaults, relevant official recipe, available resources, and the
user's purpose. Include each task even if its priority run is currently blocked. For a data-only
task, state the model input is inapplicable. Give each option a short description of its practical
purpose and outputs, the exact command or configuration, the dataset/split and model/weights,
required hardware and inputs, and the expected runtime range. Include other combinations only
when they serve a distinct purpose or resource budget. Provide an order when tasks depend on one
another. Formal execution begins for the options the user authorizes.

Use the precheck to identify the compute unit. Profile about ten representative real samples
with the proposed dataset or official split, model weights, input settings, runtime, and
hardware. Aim to finish the timing run within five minutes, including startup and precheck,
and follow the [short-run guidance](../../maintain-project/references/coordination.md#keep-setup-runs-short)
during first-time setup. Report acquisition and environment setup separately from compute
measurements. Use the completed work for the estimate.
Apply the same batch size and worker count as the proposed run. Let the last full batch
cover the sample target when needed. Include actual training and validation work within
the same limit. Use independent requests for services and consecutive frames for video
when frames are the compute unit. If the model generates whole clips, time complete clip
requests. Use all items when the entire workload is smaller and fits the limit.

Where a run has a time bound, arrange for a clean stop at that bound. Keep progress timings
for any completed items or steps and identify any unfinished outputs. State the real
sample count, workload units, elapsed time and the reason for a short sample. If the
deadline passes before any representative unit completes, report the measured stage and
the evidence still needed for a reliable full-run estimate.

Report the full dataset or split size, number of epochs or passes, batch size, hardware, and
a rough end-to-end time range for completing the whole task. Measure startup and steady-state
throughput separately, and account for scheduled evaluation, output and checkpoint I/O,
and known scaling limitations. Identify measured durations and extrapolated ranges. If the
proposed hardware is unavailable, give an estimate for a viable configuration when measured
evidence exists and state how to calibrate the other configuration. If a throughput measurement
or workload count cannot be obtained, report the specific blocker and the measurement still
required. Report download and setup time separately when material. Save the choices and their
evidence in the project's existing experiment or maintenance documentation.

## Tracking and recovery

1. Checks the running identity with the original start-up command, effective configuration, actual interpreter, device and process, session logs, outcome lists and check points. Supports the group configuration to read back the current version.
2. If you want to keep track of your work, read your logs and indicators, and wait on the tool's ability, so that you can keep up with your status.
3. Determines which results can be reused, which steps are missing and which preconditions need to be repaired. Prior to running, confirm that the current task supports recovery and differentiates between the full training status and the weights to be used for reasoning only. Checks the configuration, input, environment and historical status of the check points. If there is no resilience or necessary evidence, identify the specific missing items and give the path to running or restarting. When restoration is needed, fill the missing items with the actually responsible outcome interface.
4. Report on the real status, completed results and follow-up actions.

## Debugment and Performance

1. Distinguishing between observed phenomena, identified causes and explanations yet to be validated.
2. Select the minimum input and inspection that is sufficient to locate the problem. Use the synthesis input, small precheck, or short running when sufficient. The diagnostic file is placed at the project's specified operational information and the results of the original experiment are maintained. Use the existing back-office service switch of the project to control the testing process.
3. Performance questions are counted from the actual transfer chain to record data, equipment, workload and numerical conditions. Candidates are compared with the same input and test; local measurements correspond to local conclusions. Humans make trade-offs when results are changed in semantic, resource budget or historical comparability.
4. The project scripts are formally implemented in accordance with project practice, are subject to long-term inspection and are cleaned up after a temporary check has been completed. The restoration is confirmed by the approved regular access and the basis and scope of application are included in the mission information.

## Validation criteria

### Independent experimental inspection

- After full operation, and when repairing the result producer or receiving and inspection project, run `rh projects experiment check <project root directory>`.This command is independent of the tree-wide path check and exits on the basis of the configuration, directory identity, running list, product name, complete path and disk file for each execution check. `0` The number of checks is zero, which means that the current tree is not formally executed and delivered as it is.
- The public entry point is written down. `metadata/manifest.json` or `manifest.json`.Records `run_id`, `subname`, `status`, `effective_config`, and `outputs`, with `role` and `execution_name` when the physical path includes those levels.effective configuration Data Sets, Optional Models and Tasks `name` or a string expresses the current selection. Open identification is different from the path or configuration structure, by `component_paths` Save datasets, optional models and task paths derived from actual selections.`outputs` The key fixes the main name of the file and the value starts with the root. `artifacts/` or `reports/` Internal complete path. The home name of the product contains a full word in English and the executive number is kept in the operating record. Register every official artifact and report at its path relative to the run. Keep independently rerunnable evaluations, visualizations, and comparisons under their own descriptive experiment purpose. Their manifests name the input runs, relevant checkpoint or data identities, and the actual outputs. Keep scratch renderings in the temporary workspace until they are selected for retention.
- Move frozen experiments and demonstrations to `assets/history_experiment/<named-result>/files/`. Preserve the original files and internal paths, and document their source and readback procedure in the adjacent README. Check for active writers before moving files and verify representative readback afterward. Keep an old run in `experiment/` when the original evidence establishes its identity, effective configuration, and outputs and the run passes the independent experiment check.

- Project-wide maintenance coverage `experiment/` All existing experiments and additional experiments. First, the actual running and results group from the disk, including independent running, analysis and engineering information hidden in the product's subtree. Check the data, models, tasks, uses and performance attributions of each experiment with the original order, the validity configuration and the execution record; generate and access the type, fixed file name and complete relative path of the results for which the check is made, and read the actual document to verify the relationship. Independently run checks separately, the same product agrees that a mass check is available. `experiment/`.The reconciliation of the remaining experiments and results groups continues to be completed after full-tree inspection and individual reading back.
- When you organize an existing product, take a separate inventory of the experiment, method or role level and within each package. The current path to browse is regulated by identifying the research according to the configuration, command and results in effect. Store fold, seed, time, and attempt information as fields in the execution record. You can keep the original archive and internal format and register the original identity. The current entry to verify the old results locates the same result and reads key files.
- The path is revised to review old addresses, unknown components, temporary directories and duplicate products without users from the physical tree by group; the exception is to clear the source, depend on and access the entry.
- Checks path identification using actually readable data and exemplified models. Writes folds, numbers and duplicates into the record or product. Reads independently from the public entry point of the parent and the role when there is an independent control role. Use a controlable input to check whether the reruner parent keeps the other roles, whether the log is still in this operation, and whether the summary is read out of the corresponding discounts and indicators.
- Checks the real file from each available path, checking the location of the independent operation to write to the corresponding data, model and task, and the joint results are read along the physical analysis entry, and the movement status and project evidence are positioned by the actual user. The actual check of the entire level 1 directory of the root of the experiment and the input of evidence for each mark. After moving the historical results, verify that the normal entry is read back against the key elements before the change, and check that the new operation will also be written into the same structure.

- Matches data, models, tasks, status, indicators, necessary documents and executing identities with current valid configuration and project access. For runbacks or restorations, check which result is selected, whether the conditions will be covered or mixed, and the specific tips when missing.
- Compare the pre-operational check to delineate the participant role, model selection, calibration of indicators and coverage. Save the original conditions for historical results.

### The path or product of this operation is not checked

1. Proceeding from the path and expected results indicated in the inspection report, and in conjunction with this official order, effective configuration and disk file, locate the target project to actually determine the path or write the code of the product. Based on ResearchHarness's original checker and rules. When repairing this failure, all code and configuration changes are limited to the target item that was authorized to be maintained.
2. **Path generation error.** Amends the routing logic of the public entry point to the data, models, tasks and experimental uses actually used for this time and synchronizes the affected reading portal. Confirms that the existing products are in the current operation and moves them to the right position to preserve the reusable results.
3. **Error at product under path.** When a file is found to be ungenerated, the missing position is calculated or steps are written, and priority is given to the restoration of the item or to the completion of the entry. Only if the missing result has to be recalculated will the result be recalculated and the corresponding calculation made within the authorization.
4. **Accepts the current result and the production code, respectively.** Rechecks the results with the original checker and opens the user's product by formally reading the entry to the project. Then executes a minimum rerun from the same public entry point to cover the original error, confirming that automatic prechecking and actual writing can produce compliance, readable results. There are still deviations to continue repairing the new evidence. Only if the existing conditions do block subsequent processing will the specific results of the failure to deliver, the methods tried, the reasons identified and the conditions required for continuation be reported.

## Synchronization of the experimental report and description to humans

When the experiment is carried out, the state or outcome impact study judgement, the `doc/experiment.md` or the equivalent project page is updated simultaneously. The article-by-line project document specifications: object and judgement, operation and conditions, status and product, conclusions and uses, limits and follow-up, link to the configuration, implementation environment and operation list in effect.

The results, causes, effects, or choices to be used by the user first. Only the framework, environmental variables, algorithms, parameters, and measurement limits that affect understanding or decision are placed in the body of the document, while the rest remain on the available record. The necessary terminology is then introduced with specific experimental examples; user feedback is difficult to understand and reduces the concept presented at the same time. The reasons for this are to be found in the context of existing facts and missing evidence. Similar cases and temporary retreats support the next investigation. The performance report also indicates what is measured, where the results are applicable and what can be decided on the basis.

## Item-by-line

Repeating, seeding and digestion can be attributed to the same experiment, with a list of identities and meaningful differences. precheck, acceptance and formal results are presented in their respective statements.

The body of the experimental report presents key values, conditions for comparison and limitations.
