# Maintain a project offline

## Purpose and main functions

Use this guide to turn a maintenance request into changes that fit the project's existing file structure. Each section explains where to work and how to verify the result.

## Scope

Use this guide when `.everresearch/mode.toml` sets `enabled = false`. Work from the project's README, configuration, commands, tests, and run records, using resources available to the project.

## Choose the skill from the request

Before starting a task in the table, open the named skill if available. Use the skill supplied by your agent, open `.agents/skills/<skill>/SKILL.md` when present in the project, or run `rh guide skill <skill>` and read the file it prints. A local EverResearch source checkout also has the skills under its own `.agents/skills/` directory. These are local lookups and work without changing the project’s maintenance mode.

If no copy of a skill is available, continue local project work using the linked section and the project README. For a request that needs the named skill itself, report the missing skill. For a GitHub or Hugging Face publication or a marketplace submission through EverResearch, read the named skill before any remote write.

| When the user asks to… | Read first | Where to continue in a standalone copy |
| --- | --- | --- |
| Set up an unfamiliar project with EverResearch, check a whole project, or coordinate changes across several components | `maintain-project` | Start with [the public entry point](#start-with-the-projects-public-entry-point) and the project README |
| Change a shared CLI command, launcher, component wiring, resource selection, or result I/O | `maintain-base` | [Shared runtime](#base) |
| Add, change, or remove a dataset, loader, preprocessing, labels, or splits | `maintain-dataset` | [Dataset implementations](#datasets) |
| Add, change, or remove a model, variant, initialization, or checkpoint loading | `maintain-model` | [Models](#models) |
| Add, change, or remove training, evaluation, inference, a metric, or an automatic precheck | `maintain-task` | [Tasks and prechecks](#tasks) |
| Add, remove, or change a reusable configuration option, default, or preset | `maintain-conf` | [Configuration](#conf) |
| Run, resume, reproduce, or inspect an experiment using the available tasks and settings | `maintain-experiment` | [Experiments](#experiment) |
| Review, debug, or refactor code and trace the affected callers | `maintain-code` | [Read, investigate, and plan](#read) |
| Write a reusable helper or plot, add a regression test, or update docs or assets | `maintain-optional` | [Tests and scripts](#tests-scripts), [documentation](#doc), or [assets](#assets) |
| Try an idea once or create a disposable script, plot, or note | `maintain-tmp` | [Temporary work](#tmp) |
| Compare with GitHub, push, open a PR, publish a release or tag, or update a GitHub deployment | `maintain-github` | [GitHub publishing](#publishing) |
| Get data or weights from Hugging Face, publish a Hub dataset, or check or update a Space | `maintain-huggingface` | Use the README for local data preparation. Use the skill for Hub operations |
| Save a lesson, decision, or research idea from the conversation as a reusable note | `maintain-knowledge` | Use the skill |
| Test EverResearch on supplied projects, log or analyze maintenance decisions, or run a skills exam | `maintain-skill` | Use the skill |
| Explain the structure of a paper or codebase, or build a diagram or interactive map | `extract-structure` | Use the skill |
| Check, submit, or update an EverResearch listing in an agent marketplace | `maintain-plugins` | Use the local maintainer skill |

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

For a GitHub comparison, push, pull request, tag, release, or deployment, read `maintain-github` using the local lookup above. It gives the publishing procedure and its approval and completion checks. If it is unavailable, inspect the project’s release instructions and prepare a local diff. Store project release configuration under its root `.github/`.

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

Identify the dataset, version, required files, and directory structure from the loader and recipe. Reuse the existing version when available. Place prepared data under the shared workspace's `data/<dataset>/<version>/`, next to EverResearch and the research projects. Use the existing staging mechanism for atomic moves or resumed downloads. Check source manifests or checksums and verify representative inputs through the actual loader. Keep version and provenance information and clear completed staging files.

<a id="assets"></a>

## Keep reusable resources and caches

Identify the consumers, useful lifetime, and regeneration method. Keep extraction and index files that accompany raw data with the shared data root. Use named assets for project-owned prepared inputs, fixed question sets, cached answers or annotations, stable demonstrations, and frozen resources. Keep client caches at their configured locations. Use `assets/<type>/<resource>/files/` for named resources and `scripts/` within that resource for dedicated helpers. Document consumers, source, version, and updates in its README. Check compatibility through the real consumer before replacing an existing resource. Keep individual run results under their corresponding experiment.

<a id="third-party"></a>

## Maintain third-party code and files

Identify the declared dependency, upstream version, and actual imports. Use the normal dependency setup for dependencies available through it. Keep bundled upstream content under `third_party/<upstream>/` with its names, license, origin, and documented local changes. Keep project adapters with their responsible component. Verify the loaded version and affected behavior through the existing entry point.

<a id="doc"></a>

## Update documentation and navigation

Follow the intended reader from README or `doc/README.md` to the relevant configuration, command, or result. Keep commands, links, and examples aligned with the current implementation. Update the topic page and the navigation people use to find it. Check the path and any example that changed.
