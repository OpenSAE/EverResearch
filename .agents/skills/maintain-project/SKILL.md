---
name: maintain-project
description: Connect a scientific project to ResearchHarness, coordinate maintenance across component owners, and verify the project through its public entry points.
---

# Maintain a scientific project

## Purpose and main function

Establish how the project is used, assign each maintenance issue to the skill responsible for it, and verify that the resulting project works across component boundaries.

## Scope of application

Use for a project connection, first inspection, whole-project maintenance, or work that crosses component boundaries. Resolve a supplied project name to its registered root or uniquely matching local project. Start with the project's `AGENTS.md`, maintenance mode, and public entry points. For work within one component, use the corresponding specialist skill directly.

Apply the requested scope. A whole-project maintenance request covers applicable structural and functional issues in the target project. Preserve existing user work and supported public commands, imports, and historical result access. A request limited to registration, inspection, or a specific area retains those limits. Central ResearchHarness changes require their own authorized scope.

## Keep each responsibility in its owning file

Maintain each rule or procedure in the skill or companion file that owns the work. Give each file a distinct purpose and scope. The project entry defines when to call the owner, what evidence to bring back, and how to check that components still work together. Link to the owner for detailed instructions. When a procedure appears in more than one place, reconcile the requirements at the owner and replace the copies with links. Place supporting examples, tests, and scripts with the function they validate or implement.

## Establish the project baseline

1. Resolve the actual root, version, local changes, public commands, default configuration, available resources, and existing results. Start with the physical tree, including ignored results and workflows that still run from scripts or notebooks. Record the applicable maintenance mode and the expected result for the current request.
2. In online mode, use `rh projects maintenance <project-root>` to recover the registered entry points and existing evidence when authorized. Use `rh projects project check <project-root>` for whole-project structure and `rh projects layout check <project-root>` for a scoped layout repair. In offline mode, use the project's offline guide and launcher. If the selected online source is unavailable, report the blocker and leave the choice of switching modes to the user.
3. Trace one representative public invocation from configuration through dataset preparation, model selection, task execution, and result reading. Use additional entry points when they produce materially different outputs or call different implementations. Capture current behavior before reorganizing it. For read-only work, use the available source, configurations, and results and identify what remains unverified.

## Connect an existing project

For an authorized online connection, check `rh projects list`, register the actual project root if needed, and run `rh projects setup-maintenance <project-root> --online`. Reuse the registered identity and applicable mode when taking over an existing connection. Bind the actual local interpreter and data resources as needed, then check `rh projects status <project-id>` and the project's own `python -IS .researchharness/maintain.py status`. For an authorized new standalone setup, use `rh projects setup-maintenance <project-root>` with the project's intended mode.

Use the project’s installation and operating instructions to confirm its normal entry. Check structure and use a representative precheck or configuration preview within authorization. Deliver the connection status and separately identify unavailable scientific inputs or checks.

<a id="shared-project-guidelines"></a>

## Assign work and collect evidence

For whole-project maintenance, cover the base, data, model, task, and configuration responsibilities. Include experiments, scripts, documents, and temporary material where they are present or affected. One public run can provide evidence for several responsibilities. Record the coverage and check each additional implementation whose behavior differs.

| Responsibility | Owning skill | Evidence for project acceptance |
| --- | --- | --- |
| Public launcher, configuration synthesis, selection and dispatch, shared paths and resources | [maintain-base](../maintain-base/SKILL.md) | The real command selects the expected components, resources, and output location. |
| Dataset registration, preparation, splits, reusable derived inputs | [maintain-dataset](../maintain-dataset/SKILL.md) | The active reader gets the intended source, sample identity, and preparation or split. |
| Model variants, weight selection, construction and interfaces | [maintain-model](../maintain-model/SKILL.md) | The selected model and weights satisfy the task's input and output contract. |
| Scientific task, compatibility and its automatic precheck | [maintain-task](../maintain-task/SKILL.md) | The normal task runs its gate and consumes the selected dataset and model. |
| Public parameters, defaults, overrides and configuration documentation | [maintain-conf](../maintain-conf/SKILL.md) | Effective values reach the actual consumer, and the documented examples use the current interface. |
| Run paths, artifacts, manifests, downstream analysis and historical readback | [maintain-experiment](../maintain-experiment/SKILL.md) | Current writers produce compliant paths and usable records. Current readers can retrieve retained results. |
| Reusable implementation, consolidation, excessive directory size and compatibility | [maintain-code](../maintain-code/SKILL.md) | Actual callers use the responsible implementation, and supported commands and imports still work. |
| Standalone scripts, tests, navigation and external material | [maintain-optional](../maintain-optional/SKILL.md) | The supported standalone access, regression collection, and links work from their documented locations. |
| One-time files and cleanup | [maintain-tmp](../maintain-tmp/SKILL.md) | Temporary material has a verified disposition, and reusable implementation can be found at its official entry. |
| Evaluating or updating the skills themselves | [maintain-skill](../maintain-skill/SKILL.md) | The evaluator defines coverage and controls the independent test. The project assistant follows normal project maintenance and reports evidence from the supplied target. |

## Coordinate structural changes

- Use the central report and actual caller relationships to decide which component owns each file or group. For mixed packages, inventories, compatibility maps, and cross-component moves, follow [Project organization](references/project-organization.md). It explains how to trace the existing call chain, separate responsibilities, and verify the resulting layout. Apply it when moving or consolidating work across components.
- For naming, folder placement, and the permitted project layout, use the [ResearchHarness project agreement](../../../src/harness/projects/README.md#project-layout). It defines the shared layout and applies to project restructuring and central acceptance. For a runnable example of this layout, use the [CUB reference project](../../../src/harness/projects/templates/cub/README.md), which shows how an official command connects configuration, components, precheck, and results.
- When a change affects multiple owners, record the producer, readers, public entry points, and retained outputs before moving anything. Coordinate the source, configuration, imports, write paths, readback, and documentation as one change. Verify replacements before removing redundant files. Retain an old address or compatibility entry when an actual supported caller depends on it. If the project root changes, synchronize its registration and supported callers with the filesystem move.
- Preserve original inputs and historical identities, and verify the contents of moved material. If an active writer or insufficient disk space blocks a migration, protect that material and continue work on independent groups. Record the exact remaining path and condition for resuming.
- Use the [ResearchHarness project documentation agreement](../../../src/harness/projects/README.md#project-documentation) to verify the project index and environment page. It defines how project documentation connects current commands, parameters, components, and results, and applies when those paths or interfaces change.

## Verify and deliver the whole project

1. Run the authorized structural check again on the actual project tree. Whole-project structural acceptance requires exit status `0` and an empty violation list. Verify experiment acceptance separately when output paths or results are affected.
2. Use the representative command to check the full chain across owners. Verify effective configuration, actual data and model selection, precheck or task behavior, and readable outputs. When the change affects default, named, repeated, or batch invocation, collect the applicable evidence from `maintain-experiment`. Check that the producer creates the new layout and an ordinary reader can still retrieve retained results.
3. Preserve behavior for supported public callers. Verify the built and installed entry if packaging changed. If scientific behavior or the meaning of the evaluation would change, explain the effect and collect the user's decision while continuing independent structural repairs. Use the [ResearchHarness execution agreement](../../../src/harness/projects/README.md#project-execution) for the scope of evidence and when real execution is authorized.
4. Reuse earlier checks when the effective configuration, data, weights, and environment still support them. When authorized to update the machine index, record `entrypoints`, `issues`, and `evidence` with `rh projects maintenance <project-root> --record <json-path>`. Reassess the affected evidence when the project or its inputs have changed.
5. Report what changed, verified commands and outputs, and concrete remaining blockers. Distinguish structural success, observed behavior, and checks that require unavailable inputs or authorization. Leave component-specific repair and validation details with their owners.
