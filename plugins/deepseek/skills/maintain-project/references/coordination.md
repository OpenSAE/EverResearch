# Coordinate project-wide maintenance

## Purpose and main function

Coordinate project-wide maintenance.

## Scope of application

Use for registration, cross-component coordination, project acceptance, or resolving the existing maintenance mode.

## Keep each responsibility in its owning file

Maintain each rule or procedure in the skill or companion file that owns the work. Give each file a distinct purpose and scope. The project entry defines when to call the owner, what evidence to bring back, and how to check that components still work together. Link to the owner for detailed instructions. When a procedure appears in more than one place, reconcile the requirements at the owner and replace the copies with links. Place supporting examples, tests, and scripts with the function they validate or implement.

## Establish the project baseline

1. Resolve the actual root, version, local changes, public commands, default configuration, available resources, and existing results. Start with the physical tree, including ignored results and workflows that still run from scripts or notebooks. Record the applicable maintenance mode and the expected result for the current request.
2. In online mode, use `rh projects maintenance <project-root>` to recover the registered entry points and existing evidence when authorized. Use `rh projects project check --json <project-root>` for whole-project structure and `rh projects layout check <project-root>` for a scoped layout repair. In offline mode, use the project's offline guide and launcher. If the selected online source is unavailable, report the blocker and leave the choice of switching modes to the user.
3. Trace one representative public invocation from configuration through dataset preparation, model selection, task execution, and result reading. Use additional entry points when they produce materially different outputs or call different implementations. Capture current behavior before reorganizing it. For read-only work, use the available source, configurations, and results and identify what remains unverified.

## Connect an existing project

Use `rh projects project status <project-root>` to check maintenance readiness without running project
code. A `managed` result includes the active guide. An `unavailable` result identifies an incomplete or
broken setup. An `unmanaged` result means EverResearch maintenance is inactive for this project.
Structural checks are separate and can be run before setup.

A project without a selected EverResearch mode follows its own rules until its user authorizes
EverResearch setup. This also applies when the status command recognizes a legacy registration.
Complete setup before handing project edits back to a specialist.

For a read-only request, inspect the repository and explain what an adoption plan would change. For an
authorized adoption, identify the target root, existing user work, setup changes, and verification
steps, then carry out setup. A general request to handle the identified project with EverResearch
already authorizes default adoption. Suggestions printed by the read-only preview can inform the
work and the user's original request determines its scope. After setup, recheck status and continue
the task. For a broken connection, repair the selected mode within scope and ask the user when a
switch is necessary.

For an authorized online connection, run `rh projects setup-maintenance <project-root> --online` using the intended EverResearch CLI. It reuses an existing registration or creates one for this checkout. If that name belongs to a different checkout, register this path under a distinct name first. Verify that the project launcher reports online status when invoked from the project's usual Python. Use `rh --version` to identify the CLI and compare it with the agent's runtime when investigating a mismatch. Bind the project's Python and data only when the scientific work requires them.

For a standalone checkout, run `rh projects setup-maintenance <project-root>`. Repository maintainers can publish the generated instructions and ignore rules once. Verify consumer setup from a fresh clone using `git status --short`; mode, connections, backups, and any locally generated bundle files belong in the repository's ignore scope.

In a Git checkout, check structure against tracked files and new non-ignored files. Investigate ignored run outputs only when affected, using the project reader or `rh projects experiment check` for runs that declare the EverResearch format. Start with the relevant command and skill section for a focused request; use the operations manual as a lookup when responsibilities are unclear.

Use the project’s installation and operating instructions to confirm its normal entry. Check structure and use a representative precheck or configuration preview within authorization. Deliver the connection status and separately identify unavailable scientific inputs or checks.

## Complete default adoption

When the user explicitly asks for EverResearch on an identified project without naming a narrower
task, connect the project, make behavior-preserving repairs, and verify the result. Use an existing
maintenance mode when set. For a fresh project, select online maintenance when the current machine
has a shared EverResearch workspace for it, or standalone offline maintenance otherwise. Honor any
mode the user specifies. An explicit request for registration or read-only inspection defines its
own narrower scope.

1. Save the initial setup backup. Find the existing commands, supported imports, build and test
   configuration, and representative workflows. Use the structural report to locate the owners of
   each real component and the callers that might depend on its current path.
2. Assign layout, configuration, and documentation changes to their owners. Route public entry
   points that depend on prohibited paths to `maintain-base`. Require working components and
   configuration that preserve scientific behavior, defaults, original inputs, and existing results.
   Use [Source ownership](project-organization.md#establish-source-ownership) to assign the target’s
   existing implementation groups and keep migrating all groups within scope.
   Follow the development-path check below for installable commands and registered components.
3. Keep setup runs short as you continue independent repairs and rerun the structural
   check until it passes or each remaining item has a concrete blocker. Use the project’s smallest representative public command,
   existing test, or official precheck for the first evidence. Complete the component and task
   acceptance coverage below. Use real data and weights in bounded checks.
4. Ask for a decision only when completion requires a real change in scientific behavior, loss of
   existing work, a conflict with an interface the user explicitly requires, a required workflow
   with no equivalent replacement, a material resource or access commitment, or authorization
   outside the task. Resolve routine
   placement and entry-point migrations within the task.
   For a necessary decision, state the exact operation, existing and proposed paths, affected
   callers, and the evidence that makes the decision necessary. Complete independent work while
   that decision is pending.

## Keep setup runs short

During first-time project setup, aim to keep each actual code execution within five minutes.
Choose a short input, representative test subset, or bounded experiment through the normal
entry point. Use natural stopping controls such as sample, step, or batch limits. For a run
that genuinely needs longer, give the user its purpose and approximate duration. Follow
the user's authorization for resource commitments and any explicit time limits.

<a id="shared-project-guidelines"></a>

## Assign work and collect evidence

For whole-project maintenance, cover the base, data, model, task, and configuration responsibilities. Include experiments, scripts, documents, and temporary material where they are present or affected. One public run can provide evidence for several responsibilities. Record the coverage and check each additional implementation whose behavior differs.

| Responsibility | Owning skill | Evidence for project acceptance |
| --- | --- | --- |
| Public entry-point migration, configuration synthesis, selection and dispatch, shared paths and resources | [maintain-base](../../maintain-base/SKILL.md) | The real command selects the expected components, resources, and output location. |
| Dataset registration, preparation, splits, reusable derived inputs | [maintain-dataset](../../maintain-dataset/SKILL.md) | The active reader gets the intended source, sample identity, and preparation or split. |
| Model variants, weight selection, construction and interfaces | [maintain-model](../../maintain-model/SKILL.md) | The selected model and weights satisfy the task's input and output contract. |
| Scientific task, compatibility and its automatic precheck | [maintain-task](../../maintain-task/SKILL.md) | The normal task runs its gate and consumes the selected dataset and model. |
| Public parameters, defaults, overrides and configuration documentation | [maintain-conf](../../maintain-conf/SKILL.md) | Effective values reach the actual consumer, and the documented examples use the current interface. |
| Run paths, artifacts, manifests, downstream analysis and historical readback | [maintain-experiment](../../maintain-experiment/SKILL.md) | Current writers produce compliant paths and usable records. Current readers can retrieve retained results. |
| Reusable implementation, consolidation, excessive directory size and compatibility | [maintain-code](../../maintain-code/SKILL.md) | Actual callers use the responsible implementation, and supported commands and imports still work. |
| Standalone scripts, tests, navigation and external material | [maintain-optional](../../maintain-optional/SKILL.md) | The supported standalone access, regression collection, and links work from their documented locations. |
| One-time files and cleanup | [maintain-tmp](../../maintain-tmp/SKILL.md) | Temporary material has a verified disposition, and reusable implementation can be found at its official entry. |
| Evaluating or updating the skills themselves | [maintain-skill](../../maintain-skill/SKILL.md) | The evaluator defines coverage and controls the independent test. The project assistant follows normal project maintenance and reports evidence from the supplied target. |

## Coordinate structural changes

- Use the central report and actual caller relationships to decide which component owns each file or group. For mixed packages, inventories, compatibility maps, and cross-component moves, follow [Project organization](project-organization.md). It explains how to trace the existing call chain, separate responsibilities, and verify the resulting layout. Apply it when moving or consolidating work across components.
- For naming, folder placement, and the permitted project layout, use the ResearchHarness project agreement (open the path printed by `rh guide project-agreement` and read **Project layout and naming**). It defines the shared layout and applies to project restructuring and central acceptance. For a runnable example of this layout, use the CUB reference project (open the README in the directory printed by `rh guide example`), which shows how an official command connects configuration, components, precheck, and results.
- When a change affects multiple owners, record the producer, readers, public entry points, and retained outputs before moving anything. Coordinate the source, configuration, imports, write paths, readback, and documentation as one change. Assign public entry-point migrations to [maintain-base](../../maintain-base/SKILL.md#migrate-a-public-entry-point-that-conflicts-with-layout) and collect the replacement verification. If the project root changes, synchronize its registration and supported callers with the filesystem move.
- Preserve original inputs and historical identities, and verify the contents of moved material. If an active writer or insufficient disk space blocks a migration, protect that material and continue work on independent groups. Record the exact remaining path and condition for resuming.
- Use the **Item documents** in the ResearchHarness project agreement to verify the project index and environment page. It defines how project documentation connects current commands, parameters, components, and results, and applies when those paths or interfaces change.

## Verify and deliver the whole project

1. Run `rh projects project check <project-root> --strict` on the actual project tree and confirm an empty violation list with `--json` (or use the equivalent offline launcher). Require strict exit status `0` and an empty violation list using the current layout rules. Verify experiment acceptance separately when output paths or results are affected.
2. Inventory the supported datasets, model variants and weight sources, and research tasks
   from public commands, registration and configuration. For whole-project readiness, choose a
   small coverage set across distinct real registered models and datasets. For general
   readiness, aim for up to five distinct models and five distinct datasets if the project
   offers that many. Prefer smaller
   public resources and a pairing plan that covers both dimensions without a Cartesian sweep.
   Use the project's setup to obtain missing authorized inputs and run each representative
   precheck through its public entry. Validate the actual data loading, model and required
   weights, and report the selected model, dataset, and outcome. Use the isolated cache or
   bound resource location prepared for the test. When a selected input cannot be obtained,
   repair the normal setup path or try another supported selection within authorization.
   When the cache or accelerator has limited room, run real prechecks sequentially and
   reclaim only disposable scratch from the current check. Compare model and dataset
   selections separately to verify the achieved breadth.
   Record the concrete reason for every remaining gap. Dataset-only validation demonstrates
   the data path and reports its scope separately from a paired model and dataset precheck.
   Exercise the actual task gate for changes to task execution. Keep other coverage proportional
   to the requested readiness goal. Confirm incompatible selections are rejected where relevant.
   [Component acceptance](project-organization.md#validation-of-components-and-experimental-products)
   defines the coverage and evidence requirements.
3. Require evidence that migrated public entry points preserve the behavior of the workflows they replace. Verify the built and installed entry if packaging changed. If scientific behavior or the meaning of the evaluation would change, explain the effect and collect the user's decision while continuing independent structural repairs. Use the **Run and accept** in the ResearchHarness project agreement for the scope of evidence and when real execution is authorized.
4. Reuse earlier checks when the effective configuration, data, weights, and environment still support them. When authorized to update the machine index, record `entrypoints`, `issues`, and `evidence` with `rh projects maintenance <project-root> --record <json-path>`. Reassess the affected evidence when the project or its inputs have changed.
5. Close the ownership review against the original implementation groups. For each principal
   workflow, give the original and current locations of the actual implementation and show where
   its documented entry point resolves at runtime. Give the provenance and reason for each retained
   upstream dependency. Report structure, runtime verification, and source migration separately.
   Keep migration open for any in-scope project-owned group that still needs an owner, with the
   exact blocker and what was verified. Leave implementation details with the owning skills.
6. Mark whole-project software readiness complete when strict source structure, required
   real-input prechecks, and the affected public commands pass. Keep prior experimental outputs
   with preserved research assets and maintain their existing readers when needed. Evaluate
   full research runs, historical results, release-only evidence, and disposable artifacts
   when the task calls for them.

## Verify the development path

1. Follow the primary README in a clean checkout of the maintained source. When the project
   carries an EverResearch entry, verify repeated setup, unchanged Git status for consumer
   files, and the documented maintenance command. Put the steps for a new checkout in the
   primary README and update obsolete names, commands, and paths in the existing public
   instructions. Use EverResearch and `.everresearch/` in the normal workflow. Keep existing
   settings compatible during migration.
   Follow the contribution instructions in an
   isolated environment and run the advertised quality command. If the quality command is
   required but its dependencies are absent from those instructions, connect the existing
   package extra or declared environment to the primary contribution instructions.
2. For an extensible project, choose a representative component family. Inspect how a new
   component reaches configuration, public execution, the automatic checks, generic inventory
   tests, and packaging. Use registration as the source for both shared runtime selection and
   tests that need the full population. Keep component-specific checks with their owner.
   For tasks, follow [Add a task](../../maintain-task/references/procedures.md#add-a-task)
   and exercise the actual automatic precheck, including its worker when there is one.
   Correct duplicated inventory or discovery failures before accepting the extension.
   A bounded software test can supply synthetic inputs at the data and model boundaries
   while exercising the real task selection and worker.
3. For editable development, create a temporary component and its configuration **after**
   installing. From outside the checkout, exercise the existing installed command and its
   automatic check using that component. A passing result uses the original installation
   throughout the exercise. Verify built-package behavior separately. Remove the temporary
   sample and preserve the production fixes and a reproducible check.
4. Start with a bounded example and selected checks that demonstrate the affected behavior.
   For a software extension probe, use a synthetic component with a small result that the
   project can read back. Select a temporary location with space for the environment and outputs.
   Compare broader failures against the starting checkout when relevant. Record separately any
   original artifacts or scientific inputs absent from the distribution, and preserve their
   verification requirements when the artifacts become available.
5. Complete the software and documentation repairs that can be verified with the available
   inputs even when research artifacts are missing. A full test suite, model download, or
   release verification is optional evidence for this development-path check.
   An earlier partial maintenance record identifies remaining work. Continue through those
   uncovered entry points and fix their causes within the registered checkout's assignment.
