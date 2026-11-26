# Maintain a project offline

## Purpose and main functions

Use this guide to turn a maintenance request into changes that fit the project's existing file structure. Each section explains where to work and how to verify the result.

## Scope

Use this guide when `.everresearch/mode.toml` sets `enabled = false`. Work from the project's README, configuration, commands, tests, and run records, using resources available to the project.

## Start with the project's public entry point

Find the normal command and its inputs in the README. Follow it through its configuration, selected components, and result reader. Use a small existing example, configuration preview, or precheck when validation is authorized. The offline structure check checks the basic file layout. The project's own commands verify its dependencies, component selection, and research behavior.

Identify the user's desired input and result, then choose the relevant sections below. Use existing options for existing behavior, change the responsible component for changes to its behavior, and add a named component when the behavior has independent inputs, outputs, or callers. Trace remaining callers before removing a feature.

Use the established top-level directories and existing authorized locations. Confirm working directories and output paths before writing. Workflow setup or changes to the whole structure require explicit authorization. Preserve existing experiments, data, and user edits. After changing paths or output locations, review the paths and, when authorized, run `python -IS .everresearch/maintain.py check` from the project root.

<a id="read"></a>

## Read, investigate, and plan

Start with the specified object. Follow the normal commands to the relevant implementation, configuration, and existing results. For a failure, start with the original command, input, error, and output. Describe the observed facts and the judgments that still need evidence. Classify any diagnostic run by its purpose and the files it writes.

<a id="base"></a>

## Maintain public commands and shared runtime code

Follow public commands into `base/` for shared parsing, configuration, dispatch, and result handling. Keep algorithms with their dataset, model, or task. When changing path resolution, check how the command is invoked and where configuration is read. When changing shared result handling, confirm that existing supported results can still be read and update the relevant documentation.

<a id="datasets"></a>

## Maintain dataset implementations

Changing a data location or downloading raw files uses the existing input configuration. Changes to sample fields, preprocessing, labels, or splits belong in `datasets/`. Trace samples consumed by tasks to the dataset selector and loader, and update affected presets or task readers. Check fields, shapes, identities, labels, and splits with representative samples. Preserve raw inputs and confirm cache compatibility when changing preprocessing. Update `doc/datasets.md` and related configuration documentation.

<a id="models"></a>

## Maintain models

Follow the task configuration to model construction, weights, and outputs. Use the existing weight option for a compatible replacement. Keep variants within their model family and give independently selectable architectures or interfaces their own implementation. Before removing a variant, check recipes, checkpoints, and result readers that use it. Verify construction, loading, and the outputs consumed by an affected task. Document changes to model selection or weight compatibility.

<a id="tasks"></a>

## Maintain tasks and prechecks

Trace existing commands to task registration, computation, reports, and result readers. Extend the current task for new metrics or fields. Use a named task or subtask for independently selectable computation. Common startup prechecks belong in `tasks/precheck/`. Use the existing result writer and register new outputs in the run manifest. Define metric units, denominators, inclusion, and missing-value handling. Check a minimal valid input through the normal entry point. If precheck behavior changes, also verify that a clearly invalid input stops before computation.

<a id="conf"></a>

## Change public configuration or select existing values

Use existing overrides for a single run and the existing configuration location for a reusable recipe. Trace the real defaults, override order, and consumers before adding or changing public options. Update defaults, validation, and supported recipes together. Use a configuration preview, focused test, or short precheck to verify the actual value. Document the defaults and how to override them.

<a id="experiment"></a>

## Start, resume, or read experiments

Read prior results through their manifests and normal result reader. Before resuming, confirm the task supports resumption and check the original recipe, data, model, environment, and checkpoint. For a new run, confirm the selected resources, output location, caches, logs, and budget, then use the project's normal command. Keep run outputs with their run under `experiment/`. For failures, start with the run status, precheck report, or log. Report the run's status, result paths, and how to read them.

<a id="publishing"></a>

## Publish the project

Follow the project's own release process. Store project GitHub release configuration under its root `.github/`.

<a id="tests-scripts"></a>

## Write tests or helper scripts

Start with the normal command, existing tests, or an authorized precheck. Use `tests/` for lasting regressions, `scripts/` for reusable operators' tools, and `tmp/<purpose>/` for one-off diagnostics. Keep production logic with the relevant core component and call it through the normal entry point. Keep only repeatable tests and tools with a clear use. Clean up one-off scripts and generated files after reviewing them.

<a id="tmp"></a>

## Manage temporary work

Use the existing `tmp/<purpose>/` for temporary scripts, copies, and logs. Keep the project runnable without that directory. Use the data area's existing staging mechanism when work needs the same filesystem as the data. Move reusable materials to their responsible locations and clear the temporary files created for this task when finished.

<a id="environment"></a>

## Update the environment or dependencies

Identify the active interpreter, device, and dependency versions from the normal entry point and local bindings. Prefer a compatible existing environment. For a separate environment, use the workspace's `envs/` or the registered location. Install dependencies through the project's documented method. Verify the affected imports, device, or public command with the actual interpreter. Update `doc/environment/` when setup or runtime requirements change.

<a id="data"></a>

## Download, unpack, and prepare data

Identify the dataset, version, required files, and directory structure from the loader and recipe. Reuse the existing version when available. Place prepared data under the shared workspace's `data/<dataset>/<version>/`, next to ResearchHarness and the research projects. Use the existing staging mechanism for atomic moves or resumed downloads. Check source manifests or checksums and verify representative inputs through the actual loader. Keep version and provenance information and clear completed staging files.

<a id="assets"></a>

## Keep reusable resources and caches

Identify the consumers, useful lifetime, and regeneration method. Keep extraction and index files that accompany raw data with the shared data root. Use named assets for project-owned prepared inputs, fixed question sets, cached answers or annotations, stable demonstrations, and frozen resources. Keep client caches at their configured locations. Use `assets/<type>/<resource>/files/` for named resources and `scripts/` within that resource for dedicated helpers. Document consumers, source, version, and updates in its README. Check compatibility through the real consumer before replacing an existing resource. Keep individual run results under their corresponding experiment.

<a id="third-party"></a>

## Maintain third-party code and files

Identify the declared dependency, upstream version, and actual imports. Use the normal dependency setup for dependencies available through it. Keep bundled upstream content under `third_party/<upstream>/` with its names, license, origin, and documented local changes. Keep project adapters with their responsible component. Verify the loaded version and affected behavior through the existing entry point.

<a id="doc"></a>

## Update documentation and navigation

Follow the intended reader from README or `doc/README.md` to the relevant configuration, command, or result. Keep commands, links, and examples aligned with the current implementation. Update the topic page and the navigation people use to find it. Check the path and any example that changed.
