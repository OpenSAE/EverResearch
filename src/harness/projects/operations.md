# Project maintenance procedures by operation

## Purpose

Help project assistants carry out requests within the project's existing file structure. Each procedure explains how to recognize the operation, where to start, what to change, and how to verify and finish it.

## Scope

Use this guide for projects that follow the ResearchHarness layout. The managed section in the project's `AGENTS.md` links to each procedure. Use the project's current commands, configuration, run records, and specialist skills as implementation references. When onboarding a project, establish its current responsibilities and the authorized scope first.

## Choose the operations required by the request

1. **Identify the use case.** Find the user-facing command, expected input, and observable result. Trace the closest existing command to its configuration, responsible implementation, and result reader. When available, use the maintenance index to narrow the changes and prior evidence to review.
2. **Choose the smallest appropriate change.** Use an existing setting when it meets the request. Extend an existing component when it owns the behavior. Add a named component inside its existing top-level directory when it has an independent input, output, caller, or selection. Before removing behavior, identify the commands, recipes, documentation, and readers that rely on it.
3. **Split requests with multiple responsibilities.** For example, downloading a new revision and running an existing model usually requires data preparation and experiment execution. Add a dataset implementation change only if the input contract changes, and a configuration change only if the project needs a lasting public option. Confirm inputs, destinations, commands, and outputs for each operation. Share evidence from the same run across all applicable procedures.
4. **Resolve the destination before writing.** Work within existing compliant top-level directories and registered resources. Creating a standard top-level directory for the first time or restructuring the project requires explicit onboarding or structure-change authorization. If a write cannot be classified or its output location is unknown, use read-only investigation to resolve it.

Record the paths in scope and preserve existing user changes. After each coherent batch, compare the actual additions, moves, and generated files with the intended destinations. For an edit within an existing path, choose the smallest relevant behavior check. For changes to names, paths, or output destinations, use one authorized structure check. Use `rh projects layout check` for layout changes, and `rh projects project check` or the authorized writable `rh projects maintenance` index for project-wide checks. Correct layout violations introduced by the current work before continuing.

<a id="read"></a>

## Read, investigate, or plan

1. Start with the requested object and its current instructions, entry points, source, or results. Follow actual callers to establish evidence.
2. Diagnose failures from the original command, effective configuration, error, and artifacts. If investigation requires executing something, classify the action as result inspection, temporary work, or an experiment before proceeding.
3. Report observations, locations, and what remains uncertain. Classify any requested written deliverable under the applicable procedure.

<a id="base"></a>

## Maintain shared entry points and runtime code

1. Trace the public CLI or API to command parsing, configuration composition, component dispatch, or result handling under `base/`. Find callers such as scripts, installed commands, and tests.
2. Keep shared coordination in `base/`. Put dataset, model, and task logic in the component that owns it. Preserve existing root-level entry points, build declarations, and dependency manifests.
3. When changing path resolution, exercise the relevant working-directory or installed launch mode. If the result interface changes, check existing readers with a saved artifact. Update the affected instructions.
4. Finish when the supported entry points resolve the intended components, settings, and destinations. Use `maintain-base` for implementation details.

<a id="datasets"></a>

## Add, change, or remove a dataset implementation

1. Distinguish a data location change, a download, and a change to loading, labels, transforms, splits, or sample fields. The last group belongs in `datasets/`.
2. Trace a sample from its task back to the dataset selection, configuration, loader, and split. Reuse a preset or subset for variations of the same source. Register a named implementation when there is a distinct input contract. Identify active recipes before removing a dataset.
3. Use a small representative sample to check identity, fields, shape, labels, and split. Rebuild affected caches when preprocessing or splitting changes while preserving original input. Cover a retained old recipe where applicable.
4. Finish when the normal entry point selects and reads the expected sample and its source and version are traceable. Update the relevant dataset and configuration documentation. Use `maintain-dataset` for detailed add, change, and remove cases.

<a id="models"></a>

## Add, change, or remove a model

1. Find the selected variant, constructor, checkpoint resolution, and outputs consumed by the task. Use the existing binding for a compatible checkpoint replacement. Reuse the constructor for a same-family parameter variant. Give independent architectures or input/output contracts their own implementation.
2. Update the responsible model under `models/` and connect any needed registry entries or presets. Before removal, identify active recipes, tasks, retained checkpoints, and shared implementations.
3. Use the normal constructor or precheck to confirm model and checkpoint selection. Exercise a small forward pass and verify the outputs consumed by a representative task. Check existing checkpoint readers when the checkpoint interface changes.
4. Finish when users can select the intended model, compatible combinations work, and unsupported combinations produce a clear reason. Update model and affected configuration documentation. Use `maintain-model` for implementation details.

<a id="tasks"></a>

## Add, change, or remove a task or precheck

1. Trace the command to task registration, computation, reporting, and result readers. Extend the current task for a new metric or output field. Use a named task or subtask for a separately selectable operation with independent inputs or outputs. Keep shared task prechecks in `tasks/precheck/`.
2. Implement the computation and connect only the required dispatch and configuration changes. Write results through the existing run recorder and register artifacts in the manifest. Define units, denominators, inclusion rules, and missing values for changed metrics. Identify consumers before removing an output.
3. Run the smallest relevant case through the normal entry point and read its result back. When changing the precheck or its stop behavior, check one valid input and one invalid input that should stop before computation.
4. Finish when the normal entry point connects the task, precheck, and result readers, and task documentation explains how to use and interpret them. Use `maintain-task` for implementation details.

<a id="conf"></a>

## Change public configuration or select an existing setting

1. Distinguish a one-off override, a reusable recipe, and a change to the option, default, or meaning that callers see. Use existing overrides for one run and the established configuration location for reusable recipes. Preserve historical effective configuration with its original run.
2. Trace defaults, precedence, and actual readers. Change the responsible branch in `conf/`. Connect the default and validation for a new setting; handle retained recipes when changing semantics or removing a setting.
3. Check defaults and explicit overrides through configuration preview, a focused test, or a short precheck. Add invalid values or old recipes only when the change affects them.
4. Finish when selection works through the normal entry point and the resulting behavior is observable. Document the default, applicability, and override procedure. Use `maintain-conf` for implementation details.

<a id="experiment"></a>

## Start, resume, or inspect an experiment

1. Distinguish inspecting an existing result, reusing a run, resuming an interrupted run, and launching a new one. Read through the normal result command and manifest. Before resuming, confirm support for recovery and match the configuration, data, model, environment, and checkpoint.
2. For a new run, establish inputs, device, recipe, budget, and output and cache locations. Use the public entry point so the normal precheck, configuration snapshot, and manifest are recorded under `experiment/`. Preserve previous runs.
3. On failure, inspect its state, precheck evidence, or logs. Route missing data, invalid configuration, and implementation defects to their corresponding procedures. Read artifacts back through the public result interface.
4. Finish with the actual run status, manifest, artifact paths, and readback instructions. Report what the run actually covered. Use `maintain-experiment` for tracking and recovery details.

<a id="tests-scripts"></a>

## Write tests or scripts and decide what to keep

1. Find a current test, public command, or precheck that can reproduce the behavior. Extend an existing case when it only needs a new input or assertion. Use a temporary probe when the behavior is still being investigated.
2. Put durable automated regressions in `tests/` using existing discovery conventions. Put reusable commands with a human operator in `scripts/`. Keep one-time probes in `tmp/<purpose>/`. Scripts call the real implementation and tests use small inputs or fixtures with actual users.
3. After running, move production logic to its responsible component and connect the normal entry point. Keep stable assertions that protect a meaningful behavior or failure as regression tests. Retain a thin script when it has a recurring user and document its inputs and outputs. Remove completed one-time probes and their output, or archive evidence the user needs at its proper destination.
4. Finish when the retained test is discoverable and runnable, scripts are useful from their documented entry point, and production behavior is independent of the temporary directory. Check test collection when discovery paths change. Use `maintain-optional` and `maintain-tmp` for implementation details.

<a id="tmp"></a>

## Create and clean up temporary files or code

1. Prefer an existing precheck, reader, or test when it can answer the question. For a one-time probe, put scripts, sample copies, output, and logs in a named directory under the existing `tmp/`. Confirm where tool side effects will land.
2. Temporary scripts can call public interfaces. Keep production code, configuration, tests, and docs usable without the temporary directory. Stage data operations that need atomic moves on the data filesystem.
3. Move useful implementation or evidence to its appropriate permanent location and verify it there. Keep only the materials needed for recovery or authorized evidence, then clean up this task's temporary files.
4. Finish when the official entry point has no dependency on the temporary work and necessary evidence can be found at its permanent destination. Use `maintain-tmp` for details.

<a id="environment"></a>

## Update the runtime environment or dependencies

1. Identify the actual interpreter, device, and installed versions from project declarations, resource bindings, and the normal entry point. Verify missing packages with that interpreter. Record public dependency changes in the existing dependency declaration and local interpreter changes in the resource binding.
2. Reuse a compatible environment where possible. Put an independent environment in the parent workspace's `envs/` or its registered location. Use the project's install command or `rh projects install` with its declared dependencies. Confirm the target and other users before changing a shared environment.
3. Verify the relevant import, device, or entry point using the selected interpreter. Update `doc/environment/` when the installation or runtime requirements change.
4. Finish when the resource binding, dependency declarations, and real launch use the intended environment.

<a id="data"></a>

## Download, extract, or prepare data

1. Derive the needed dataset, version, source, file list, and layout from its loader and recipe. Reuse an existing matching copy when available.
2. Set the destination and staging location before downloading. Use the existing `data/<dataset>/<version>/` or a registered data root. Keep staging needed for atomic operations on the data filesystem. Use the local client configuration for shared Hugging Face caches.
3. Verify the download or extraction against available checksums or file lists, then open a representative sample and check its split with the actual loader. Route format changes to dataset implementation. Record the source and version and clear staging specific to this task.
4. Finish when the project can select and read the prepared data and each staging or cache path has a clear owner.

<a id="assets"></a>

## Keep reusable assets and caches

1. Identify the reader, reuse across runs, and regeneration method. Keep dataset-specific preprocessing caches with the data version, client caches at their configured locations, and run-specific scores, predictions, or checkpoints with their run. Put fixed, independently reusable resources such as lookup tables or frozen transformations in `assets/`.
2. Group resources under `assets/<type>/<resource>/`. Put resources in `files/` and resource-specific scripts in `scripts/`. Add a README explaining source, version, reader, and update procedure. Put general preparation logic in the component that owns it.
3. Use the real reader to verify path, version, and format. Keep existing resources when active callers need them and update selection at the actual reader when switching versions.
4. Finish when a normal caller can locate the right version and reproduce its provenance. Use `maintain-optional` for asset handling.

<a id="third-party"></a>

## Maintain third-party code and files

1. Identify the dependency, upstream version, and actual imports. Use the environment procedure for installed dependencies. Maintain existing vendored content under `third_party/<upstream>/`.
2. Preserve upstream naming, license, and provenance, and record local differences. Keep project adapters in the responsible component or runtime. Find supported callers before changing upstream versions or entry points.
3. Verify which version the project actually loads through its normal entry point and update the source and usage documentation. Finish when the upstream source, version, adapter, and real caller are traceable. Use `maintain-optional` for details.

<a id="doc"></a>

## Update documentation and navigation

1. Follow the user-facing README or `doc/README.md` to the page that explains the actual command, defaults, inputs, output, and paths. Update an existing page when it serves the reader; add and link a named page for an independent topic.
2. Update each affected component, configuration, task, environment, or experiment page in the same change. Use existing commands and reproducible small inputs for examples. Preserve the facts and effective configuration of historical runs.
3. Check changed links, example commands, and result paths from the reader's entry point. Classify and authorize any example execution according to its actual operation. Finish when users can find the right command, prerequisites, settings, and result reader. Use `maintain-optional` and the project manual for documentation conventions.
