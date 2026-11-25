# Example of Engineering Work

## Purpose

A true catalogue, procedures and products are used to explain how the project adds functionality, inspects changes, compares performance and presents humans for review.

## Scope

The common requirements of the agreement are presented to your superiors. projects/README.md#project-execution,Specific orders are available on the project. README.md.

## Position files from job needs

| Work | I'm in charge. | Where do you see the effects when you're done? |
| --- | --- | --- |
| Support another input | Add a new responsible module under dabasets, select the input in the configuration and entry | precheck sample shapes, labels and source fields |
| Add Model or Header | Adds a new realization under Moders, selects the model at the normal entrance | Confirm that the model can be completed in reverse and re-run the relevant model check using the existing precheck |
| Modify cross-component indicator | tasks/classification/operation.py and report reader | Comparison of original new loss, accuracy rate and results format of the same sample |
| Modify Run Resource Settings | runtime/config.py with the selected running formula | Query for actual equipment, dependence and thread settings in the running list |
| Adjust Results Formatting | runtime/records.py and the reading list entrance | Confirms the read conditions of the caller against the saved list and inspect output |

## Example request: Add per-class accuracy to the classification report

1. Trace `python -m cub_template run` through `conf/config.yaml` and `tasks/classification/task.py` to the evaluation in `operation.py`. The request extends the existing task and result, so it belongs with the classification implementation.
2. In the final evaluation, collect correct predictions and example counts by label. Keep the overall accuracy and loss. Use the existing `run.report("evaluation", ...)` call so the run manifest continues to identify `reports/evaluation.json`.
3. Check the computation with fixed labels and predictions. Two classes with counts of two and one, and one correct prediction each, should report one half and one respectively. Decide how to represent classes absent from the batch. Add a focused regression if the assertion has lasting value. When authorized, run the existing single-epoch synthetic recipe and use `inspect` to locate and read back the report.
4. Update `doc/tasks.md` with the metric definition and `doc/experiment.md` with the readback instructions. This is an implementation example. The current template reports aggregate metrics.

## Maintenance skills matching hands-on operations

When checking the template as a whole, you follow the configuration, component, precheck and results from the README official command. After access to ResearchHarness, the whole project is checked at `maintain-project`, the functional review of the assigned code is reviewed at `maintain-code`, the open parameter changes are used at `maintain-conf`, and the running and results review is reviewed at `maintain-experiment`. The following actions indicate where each starts from the template.

| Operation | Where to start in the template | How do you judge the process is complete? |
| --- | --- | --- |
| Add a source of data | `datasets/cub200/dataset.py`, offline samples from the same directory and `conf/config.yaml` | Once a new source has been selected, the official pre-test can use a representative sample and record the actual source |
| Modify a model variant | `models/residual/residual18/specs.py`, `conf/config.yaml` and actual use of the preset formulation | Check changes from effective configuration and precheck output and check with the series to keep the changes as needed |
| Indicators for the revision of classification tasks | `tasks/classification/task.py` with `operation.py`,Then track the result to write and `inspect` | Reports and inventories locate indicators that run at the same time and record meaning and historical comparability |
| Remove an option or component | Default configuration, aliases, formulae and direct call from the corresponding register | Updates the call and removes the selection. Discharges, descriptions and checks are processed when the entire component is removed |
| A diagnostic experiment. | Read the runlist from `inspect` and locate input, task or public run layer following the failure phase | Obtaining a basis for treatment from an independent pre-test or small-scale operation, and then locating the actual product from the inventory |

## Extension path from SAEBase

| SAEBase's public entry point | Templates Correlation | Practical approaches to expansion |
| --- | --- | --- |
| conf/config.yaml It's... Hydra defaults | conf/config.yaml Select and define the dataset, model, task group in the same file | Increase model configuration to switch with default configuration to overwhelm |
| models/plugins.py,tasks/plugins.py with saebase/registry.py | Plugins.py and base/cub_template/registry.py for the three components themselves | A series of statements and configuration presets for the same variant to register and read the existing series |
| tasks/capture/task.py with operation.py | tasks/classification/task.py with operation.py | task.py to perform validation and running interface, operation.py to perform task calculation |
| tasks/precheck/task.py, gate.py and saebase/runner.py | tasks/precheck/task.py, gate.py and base/cub_template/runtime/runner.py | You can select a precheck on your own and train to leave an automatic precheck check back on the same path. |
| saebase/results.py and runtime/experiment_results.py | base/cub_template/contracts.py with runtime/records.py | Task returns EvaluationResult, Run Layer Saves Results and Lists |

Adds new variables to the same series only models/residual/residual18/specs.py and conf/config.yaml. Select renet18_mlp_small from the default configuration, run prechecking and training, and read the options and reports in the list. The two variants share model.py, the same registration and classification tasks. Use your own directory when adding the official data set and update the preset for dataset registration and configuration.

The prechecking of this template is carried out in the same process, using a sample of training in the field, to check the formal steps, and to isolate the random state before starting the training.

## Samples of changes achieved: use of realistic measurements to determine the number of work processes

The classification task provides a fixed training sample view and a physical forward. `tasks/precheck/timing.py` Synces CUDA, `tasks/precheck/performance.py` compares the current number of work processes and candidate values of the formulation. Default actual formulation uses 32 graphs, preheat once, repeat three times.

Each separate recording of loader start, waiting for data, forward and data transfer, off, total time spent and GPU The pre-test locates the bottlenecks by the median of the baseline stage and reports the sample, the number of repetitions, candidate time and consistency output. logits Within given error, predictive category consistent, available CUDA If you have a visible budget and you have a faster candidate, you will be recommended, otherwise the current configuration will be followed. `--set runtime.workers=<Value>` Select the recommended value to validate the official task cost. The partial forward comparison ranges are saved with the report.

Default precheck uses the number of formally configured work processes, updates the parameters of a maximum of two graphs for the training view and evaluates them on the definitive training view. When the formal formulation appears at the end of a single chart, precheck the extra run batch is included in the list before the formal training begins. Formal training is re-initiated. When you have to limit the time of the wall clock for the full precheck order, you can use external `timeout --signal=INT --kill-after=10s 120s` time to include indexing and model preparation. The aborting record is `partial` and the list left after the mandatory termination `running` indicates that this operation still needs to be checked.

When the candidate fails in actual operation, the performance report saves the completed baseline, the reason for the failure and the decision to keep the current configuration. The running list records contain the actual model settings for the series of default values, which will allow subsequent comparison with the formula and the results.

## Human sample: introduction of new initialization

The current baseline uses random initialization. If you propose the introduction of external pre-training weights, record sources, training data ranges, additional downloads and training costs, and indicate how it compares with the original baseline. Caltech officially points out that CUB images overlap with ImageNet, which affects the interpretation of results using ImageNet weights.

## Project update with central

Keeps the version of the agreement, the actual location and the evidence of representative operation. The new item can copy the complete directory, first by consolidating the normal entry for the input exercise, and then replaces the responsible data set, model and task section. The agreement contains a disagreement or multiple questions, and records the true case, the proposed modification or the achievement of the affected caller, and returns to the central maintenance. The list of the project operations follows the protocol field, and the existing inspect provides readable results.

When the central agreement is updated, the corresponding realization, directory, configuration, or application instructions in the template are maintained on the same occasion. The cross-reference to the directory rules is this item. README.md.See the default configuration of the project conf/config.yaml,For effective configuration see experiment It's a counterwork, normal access return and component border check directly. tests.When there is an independent integrated test or a stable regression test group, then they are classified as agreed separately. ] integration or product.Sync entry, configuration of references and location of detection after moving files.
