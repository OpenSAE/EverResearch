# Experimental Programs

## Purpose

Sets the formulation selection, single parameters and experimental execution, tracking, recovery and debugging to the actual document and entry point.

## Scope

The root of the experiment is the project-level catalogue `experiment/`, which is extrapolated from the project. Projects can register their internal level and their equivalents for reading access.

## Attribution of files

| Location | Responsible content |
| --- | --- |
| `main.py`, project package `cli.py` or `__main__.py`, `tasks/workflows.py` | Reads command parameters and selects normal operations. The actual calculation goes to the corresponding task |
| `conf/config.yaml` or default entry for items | Organize a default set of configurations, select data, models, tasks, workload, equipment and input root |
| Project packages `runtime/config.py`, `runner.py`, `environment.py`, `records.py` or equivalent modules | Synthetic configuration, distribution of tasks, collection of physical environment, preservation status and product reference |
| `tasks/precheck/task.py`、`gate.py`、`timing.py`、`performance.py` | Independent precheck entrance, official job call, stage timer and candidate comparison |
| Item root `experiment/` | Select or group as necessary. The name of the executive layer describes the purpose or the control role. The duplicate execution of the same use is distinguished by the running list. Seeds, dates and other operational parameters are entered into the valid configuration or execution record. |
| `experiment/<dataset>/<task>/<experiment-name>/` | Direct analysis of the scientific products of the data. Joint analysis locates its actual master data or the joint input statement of the public entry point, and the list registers the actual sources on a case-by-case basis |
| Operation records used for the project movement entrance | Keeps the members of the movement, their progress, and their identity. |
| Project entrance for inspection | Explains the evidence needed for the experiment and repeats it as it is operational. |
| One run `config.yaml` or item equivalent file | Saves the actual effective value, the list points to the document |
| Run directory `metadata/manifest.json` or item equivalent entry | Positioning of actual configuration, input, environment, state, failure and product of the current round |
| `logs/`, `reports/`, `artifacts/`, `tmp/` for running directories | If you want to save a process log, readable results, model products and ad hoc diagnostics. |
| `scripts/`、`tests/` | Manual script calls are formally achieved. Behaviour checks that require continuous regression are required to enter the test directory |

## Configure maintenance

1. The **position effective value.** tracks the project's default entry and actual command to the configuration synthesis code, identifying the source of the parameters, the order of their overlaying, and the actual reading field. The project can use a configuration group set of default configurations, where the default values are concentrated. Check the official tasks and prechecks affected by the default changes, and view the synthesis results using the read-only method supported by the project.
2. **Changes by purpose.** Changes in the general default value of the item by `maintain-conf` Process. A single search overwrites the parameters by a formal command, or `experiment/<Data Set>/<Model>/<Tasks>/<subname>/` Saves the input configuration specific to the experiment. Organizes this type of operation with the main method or actual research purpose. `capture/non_whiten/` As a catalogue of experiments; when comparing different batches, each operation shares the same experiment name and the batch values are viewed from their respective configurations.
3. The **logs the configuration of the running time.** running portals write the actual selected components, merged defaults, visible overlays, parsed input paths and equipment into the run `config.yaml` or the item equivalent file, and directs the list to it. Use the public entry point settings of the project to confirm the transmission to the actual reader and select a read-only check or precheck as per this mandate.
4. **Check history and run back..** Interprets the current effective configuration from the respective list when the indicator or comparison is running. Reruns with the original configuration as input, checking the source code, data and environment, following the same pattern `subname`.If you perform a new research use or a control role, save it under the name that describes the difference. If the purpose and role are the same, the execution record is kept and the product is registered separately.

## Execution and Results Reading

1. Invert commands, formulations, inputs, model weights and budgets from the results to be used by the user. View the actual effective configuration by the project entry, recording the visible overlay value, the data input root and the position of this operation in `experiment/`.
2. Starts by calling the `precheck` public entry point automatically. Each time you use the current data, model and task selection to check the actual operationality, plan output path, sample file format and official read-back with a minimum sample and step-by-step check. After the precheck, you enter the formal computation. If you fail, you will automatically review the link that is responsible for the wrong recovery of the target project from the same entry point.
3. The log position of the front desk records the session identity, command, valid configuration, log and directory of operations in the manner that the project already has. The actual entry of the identity, code version or summary, interpreter, device and numerical conditions is recorded.
4. Confirms that the list status corresponds to the actual document, and reads the required characteristics and explanations, generation of content, intervention results, evaluation indicators or training reports and weights. Partially completes retain the completed results and indicate missing items and subsequent reading or calculation.

## Tracking and recovery

The current running index only indicates the current selection, and progress is based on the corresponding running evidence.

| Actual situation | Method of processing |
| --- | --- |
| The process is still operational and progressing | Follow the same process, log or indicator. Wait and check the real results according to current task |
| Completed and all results completed | Read the product from the list. When a follow-up analysis is required, hand over the configuration, input and results of the same operation to the analysis portal |
| Output missing a step | Identify the step 's input and dependencies. If you have a formal segment operation, only the corresponding step is added and the source link is saved. |
| Training stopped at the checkpoint. | Identifys the recovery parameters and load realization of the mission, checking the number of wheels, steps and random status of the model, optimizer, scheduler and the logical restoration. Checks the original configuration, data identity and software environment and runs as authorized |
| Only final model weights | If you want to renew your training, confirm whether there is a formally supported training status. |
| Operation status stopped by user | Keeps the decision. Reads the status and results and follows a clear follow-up mandate when new start-up or restoration takes place |
| Missing evidence or path failure | Continue positioning from the operational directory, log and registered input. |

The current session is monitored on an ongoing basis as mandated.

## Debug and Performance

1. Commands, configurations, input identities, operational phases and error reporting logs when a fixed problem occurs. The determination of responsibility follows the actual call. Data access and sample questions follow `datasets/`, construction and weight questions follow `models/`, indicators and task calculations follow `tasks/`, distribution, environment or list questions follow the public operating layer.
2. Select the minimum input directly related to the failure. The temporary directory of operational information is temporarily reproduced and the responsible file is formally restored.
3. The performance is prepared for pre-detection, reading or waiting, equipment transfer, computing and preservation. The walk-in device is synchronized at the time boundary. Recording the actual configuration, sample, preheat, repetition, environment, resource peak and maximum stages. Only the candidates for the same input, workload and outcome are compared, with the end-to-end impact, respectively.
4. An error record indicates the known cause, impact, and way of positioning. The report indicates which cases and circumstances are covered.

## Operations in reference items

Yes. CUB templates, with `python -m cub_template precheck --subname offline_check --set dataset=synthetic --set runtime.device=cpu` Run offline precheck. The program automatically writes the results to the root of the item `experiment/`.Command to return to the running directory, use `python -m cub_template inspect <Run Directory>` Read `metadata/manifest.json`,Finds the actual report along the output role. Compares the number of work processes with the same formulation `benchmark`,Result by `tasks/precheck/performance.py` Generates. The template currently exports the final weight, and the reader will use and rerun the results according to available capacity.

This command takes the default value from `conf/config.yaml` and only covers datasets and devices for this precheck. Saves the merge result for `config.yaml` in the running directory, and the list field `effective_config` points to the file. When running again, the file is sent to `--config`, along with `--subname`.
