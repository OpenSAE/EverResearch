---
name: maintain-project
description: Onboard, review, or maintain a research project. Follow its public entry points through layout, configuration, datasets, models, tasks, prechecks, and saved results, using the relevant specialist skills.
---

# Maintain a research project

## Purpose

Keep a project's public commands, directory responsibilities, components, configuration, and results connected through the paths researchers actually use. Inspect the whole project, use the relevant specialist skills, and recheck the user-facing workflow after changes.

## Scope

Use this skill when onboarding an unfamiliar repository, reviewing a whole project, reorganizing its source tree, or changing behavior across components. Use the specialist skill directly for a request limited to one responsibility. Read-only review, file changes, execution, downloads, publication, and research runs follow the current authorization.

## Start from the actual users and entry points

1. Identify the project root, local instructions, dependency declarations, configuration, and active commands, scripts, workflows, or notebooks. Record the source revision, relevant local changes, and existing results. Preserve research inputs and existing user work.
2. For an already connected project, check its registration, shared skills, and local resources with `rh projects list`, `rh projects status <project-id>`, and `rh projects resources <project-id>`. When onboarding, use the checkout that contains the user's current work. Apply the requested connections, then continue the project review within scope.
3. Run `rh projects project check <project-root>` as the first structural check for an identified project. Record the actual paths, rules, and expected locations. Recheck the full tree after changes. Layout passes when the command returns zero with an empty `violations` list. Review any `directory_reviews` entries by checking their responsibilities and callers.
4. Trace representative public entry points through effective configuration, dataset selection and reading, model construction, task dispatch, precheck, result writing, and readback. Trace active reports backward to their originating commands and inputs. Use [project organization](references/project-organization.md) to identify actual owners and plan migrations.

## Lay out the code and configuration

Follow the [project layout rules](../../../src/harness/projects/LAYOUT.md), the [engineering protocol](../../../src/harness/projects/PROTOCOL.md), and the [documentation guide](../../../src/harness/projects/DOCUMENTATION.md). The [CUB template](../../../src/harness/projects/template/README.md) demonstrates an entry point, components, prechecks, and run records. Apply the current rules where the template differs.

- Give the project root a purpose-driven PascalCase name with two or three words and at least one complete English word. Name project-owned files and directories after their jobs with underscores between words where needed. Reserve version digits for real data or model identities and preserve names owned by frameworks and upstream packages.
- Provide physical top-level `base/`, `datasets/`, `models/`, `tasks/`, and `conf/` directories. Put shared interfaces, dispatch, and runtime code in `base/`. Give each research component its own actual implementation in the corresponding directory. Put automatic startup diagnosis in `tasks/precheck/` and implement research computation in separately named tasks. Have public commands load `conf/config.<format>`.
- Follow every still-supported reproduction command to its actual dataset preparation, model construction, training, evaluation, and analysis. Move each implementation to the directory that owns it. Keep script entry points focused on orchestration and argument forwarding. Preserve supported imports and installed commands through package mappings or thin compatibility entry points. Recheck both source and installed entry points when applicable.
- Use `maintain-code` to check `base/`, `datasets/`, `models/`, `tasks/`, and active `scripts/` and `tests/` for misplaced, duplicated, or fragmented implementations. Check each level of `base/`, `tasks/`, `scripts/`, `tests/`, and recognized legacy source trees for the limit of 15 directly contained files. Review directories with more than 15 direct subdirectories. Dataset and model trees are governed by component responsibilities and path rules.
- Confirm each active configuration branch against its actual reader. Keep one configuration file per branch at the approved depth and keep source mappings, defaults, precedence, and `doc/conf.md` aligned. Use actual runtime configuration and result paths to verify changes.
- For an existing name or layout migration, account for current work, registered paths, resources, public imports, and current results. Preserve old commands or addresses where the project still supports them through a compatible mapping. When switching a registered checkout requires additional permission, preserve the original checkout and report the verified candidate and the exact switch still needed.

## Inspect mixed directories and existing runs

When a path is rejected at the directory level, inventory its actual contents before moving them. Then rescan to reveal any previously unvisited paths. For whole-tree reorganization, include ignored paths, snapshots, and saved runs in the inventory. Group files with the same purpose and destination, and identify individual exceptions.

| Material | Where it belongs |
| --- | --- |
| Active research and runtime code | The corresponding `base/`, `datasets/`, `models/`, or `tasks/` directory |
| Independent tools and reusable tests | `scripts/` or `tests/`, with real callers or coverage |
| Project documentation and documentation builds | `doc/`, with named documentation sites under `doc/code/` and their existing build structure preserved |
| Frozen runs, demos, and historical outputs | `assets/history_experiment/<named-result>/files/`, with their original contents, provenance, and readback instructions |
| Active experiment runs | `experiment/`, with an effective configuration, run manifest, and declared outputs that match the physical paths |
| Small temporary work or material awaiting disposition | A named directory under `tmp/`, with its origin and outstanding decision recorded |

Run `rh projects experiment check <project-root>` in addition to the project check. Inspect the physical experiment tree, including results ignored by version control. Verify each run's dataset, optional model, task, research purpose, execution role, and run ID. Track default and batch output paths from their producers to actual readers. Fix both producers and consumers when migrating. Preserve frozen configurations, source snapshots, and original results as historical evidence. Verify whether retained or migrated results still open through the actual reader.

Zero reported runs means the scanner found no formal execution records. For projects that produce research results, obtain a bounded run and readback through the public entry point when authorized, or use an existing run with adequate original evidence. Report precisely which data, weights, tools, or devices prevent a remaining execution.

Inspect active documentation and experiment reports for commands that still reference old paths. Check working directories, arguments, configuration overrides, and result links against their real callers. Prefer existing offline commands, configuration previews, and current result readers when those establish the needed behavior.

## Review each applicable responsibility

| Responsibility | Skill and evidence |
| --- | --- |
| Base runtime | `maintain-base`. Check launch, configuration composition, component choice, dispatch, resources, and result paths from the actual supported entry points. |
| Datasets | `maintain-dataset`. Trace source, preparation, splits, and representative samples consumed by tasks. |
| Models | `maintain-model`. Check model construction, variants, weight sources, and task-facing inputs and outputs. |
| Tasks | `maintain-task`. Identify public execution paths, prove automatic precheck, and verify a supported combination and a clear rejection path. Check actual computation and result readers. |
| Public parameters | `maintain-conf`. Verify the meaning, default, and override behavior at the actual consumer, and keep `doc/conf.md` in sync. |
| Experiments | `maintain-experiment`. Check effective configuration, on-disk result paths, saved records, and the conclusions supported by actual runs. |
| Scripts, tests, documentation, and external material | `maintain-optional`. Identify actual users, verify working entry points and links, and check ownership and reuse. |

Open each applicable skill and follow its specific instructions. For a whole-project review, check the base runtime, datasets, models, tasks, and configuration even when the first layout scan finds no issues. Record actual applicability for optional responsibilities. Use `maintain-code` for cross-component duplication, missing behavior, and ownership. Use `maintain-tmp` for one-off engineering work and `maintain-skill` when the user asks to evaluate the skill itself.

For each responsibility, record the actual entry point, observations and supporting evidence, actions or outstanding gaps, and verification status. Use shared evidence across responsibilities where it applies. In a read-only review, provide these findings directly to the user. For a plan-only request, give the priority order, actual changes needed, dependencies, and acceptance criteria.

## Verify the research workflow

- Trace each active mainstream command and reproduction workflow to its current implementation. Identify commands for history readback and those with unclear consumers.
- Confirm that each public execution path calls the same automatic precheck before full computation, including supported devices, alternate scripts, and batch jobs. For a supported combination, use few real inputs and the production data loader, model builder, task steps, and result writer and reader. For a known incompatible combination, verify the diagnostic and the blocked computation. Check configuration previews and help through their appropriate read-only paths.
- Trace a metric back to the actual samples, model, and evaluation protocol. Identify which samples and labels were used for preprocessing, training, early stopping, model selection, and final scoring. Record confirmed reuse and its impact separately from unresolved overlap or unmeasured impact.
- Verify `doc/environment/README.md` and its direct link in `doc/README.md`. Check that actual installation, execution requirements, data preparation, lightweight checks, and recorded execution environments match the instructions. Keep applicable component and parameter documentation current.
- Sort work by impact on current users, dependencies, and effort. Keep file organization evidence and changes to research definitions independently reviewable. If a central rule appears to misclassify a path, report the command, rule, path, evidence, and impact, and complete work that can proceed independently.

## Deliver the results

Record the final project and experiment scan statuses, remaining violations, and the number of runs checked. Summarize the seven responsibility reviews and identify the representative public commands, affected implementation paths, actual checks, and supported conclusions. List how ambiguous directories and still-used reproduction workflows were handled, with original and final locations and evidence of readback. For incomplete work, name the missing resource or decision and the specific workflow it affects.

Read the final project tree from disk. Put a separate two-level tree in the response for each project, including every visible top-level directory and its direct subdirectories. Omit hidden directories and Python caches. Identify the actual root used for the review if an old address resolves to it or a candidate checkout was inspected.
