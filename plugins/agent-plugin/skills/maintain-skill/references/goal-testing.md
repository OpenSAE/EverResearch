# Independent project testing and goal-driven repair

## Purpose and main function

Test routine project adoption, use real failures to improve EverResearch across comparable projects, and deliver accepted projects as reusable templates.

## Scope of application

Use this sequence for routine testing of supplied projects or for a confirmed maintenance goal. The waiting and timeout procedure also applies to other independent repair tests started by `maintain-skill`.

In a source checkout, keep `goal/<goal-name>/` inside this skill's local directory. In an installed release, locate the writable directory with `rh guide skill-state maintain-skill`. Use a purpose-based name for each goal or routine batch. Keep source revisions, original packages, evidence from each round, and acceptance results separate by project. Keep these records out of commits and published packages.

## Resolve sources and set acceptance

1. Resolve each supplied project to its authoritative upstream repository or source package. For an article, check the authors' code availability, linked project page, or artifact release. Record the article-to-source mapping and the revision. When no implementation can be found or several materially different sources fit, report the evidence and the exact missing choice. Continue with sources that are clear.
2. Use routine acceptance directly for a short invocation without a stated focus. For a focused request, propose a general user outcome with observable acceptance evidence and confirm it with the user before starting tests. Track each project's results separately and proceed in the supplied order. Record any template exemptions for handoff after acceptance.
3. Download a new project into a directory created for the test. Use the existing directory when the user supplies a local checkout as the target. Under `goal/<goal-name>/`, save an original package before maintenance begins. Record its source, revision, archive SHA-256, initial state, and reproduction evidence. Verify that the package extracts and keep it separate from the project directory where the subagent works. For a template candidate, save the original as a ZIP so the same file can travel with the template.
4. For a routine test, use current EverResearch for the first round. When a confirmed goal includes a reproducible failure, use the baseline to trace the cause through skill selection, commands, resources, public entry points, and result readers. Apply authorized shared repairs in the owning skills or implementation. Keep the case-specific material with the project or in the local goal evidence.

## Start the first test round

1. Set the subagent's working directory to the downloaded project or the existing target chosen above. When the test specifically begins from a saved original package, extract that package into a new directory and use the extracted project as the working directory. Make EverResearch available through its normal discovery and execution paths. Before dispatch, configure the working location, permissions, and other conditions the user would normally supply. If the test covers automatic registration or resource setup, leave that setup for the subagent.
2. Launch a new subagent with a clean conversation and the short standard task. For project maintenance, give exactly two lines.

   ```text
   maintain-project
   <ProjectName>
   ```

   For another skill, use its name and the target identifier. Keep the goal record, known failures, proposed changes, acceptance answers, and evaluator notes outside the subagent's view. The subagent works from the project's normal entry points.

## Wait for the independent agent

Start a timer when the subagent begins. The default is **60 minutes**. Until it finishes or the timer expires, the evaluator only waits. Leave the subagent, EverResearch, and the test workspace alone. Review intermediate evidence after the subagent stops.

If the timer expires without a final report, pause the subagent or interrupt its current turn using the host's available control. Keep its context and working files. Then inspect the elapsed work and determine why it timed out.

- When the delay exposes a broken rule, poor routing, repeated ineffective work, or another avoidable problem, record the cause, improve EverResearch, and dispatch a fresh subagent to continue from the current project checkout.
- When the subagent is following the workflow and legitimate work needs more time, resume the same subagent with its existing context and checkout. If the host requires a prompt to resume it, give only a neutral instruction to continue. Allow one more hour. Repeat the same timeout check at each hourly boundary until it completes or the evidence calls for a repair.

## Review a round and continue repairs

After the subagent finishes, inspect the actual changes, the normal entry points, and the results that downstream users can read. Compare them with the original evidence and the agreed goal. Check applicable routine acceptance criteria, including file completeness and preservation, working public commands, and whether the subagent independently downloaded and installed required resources when that is part of the authorized workflow. Record actual evidence and any remaining issues.

Routine acceptance follows [whole-project verification](../../maintain-project/references/coordination.md#verify-and-deliver-the-whole-project). Require strict layout, applicable real data and model checks, working required task prechecks and public commands, and reusable results with the commands and settings that produced them. Apply an agreed focused goal in addition to these checks. Projects exempt from template delivery follow the same acceptance.

When an issue remains, identify its cause and improve EverResearch. Start a new clean-context subagent with the same standard instruction on the current problem checkout so it can continue the repair. Apply the same waiting rule. Repeat until all known issues meet the goal and the applicable acceptance criteria on the working checkout.

## Accept the goal from the original package

If the first round starts from the recorded original state and passes, use that result for acceptance. After any repair rounds, extract the untouched original package into a fresh test location and use a new subagent with only the same standard instruction. **That same subagent must solve all the issues in one round from the original state with the same EverResearch revision.** A legitimate long-running task may resume under the timeout procedure in that same round. If a later shared repair affects a previously accepted project, recheck it from its recorded original revision with the final EverResearch changes.

If fresh acceptance exposes a remaining issue, return to the repair loop and repeat the original-package test with a fresh subagent after the next change.

## Deliver the template and remove the local test project

1. After fresh acceptance, put the accepted source and any evidence needed by a documented workflow in the template before removing the working copy. Follow [Project uninstallation](../../maintain-project/references/uninstallation.md) to remove temporary EverResearch registration, bindings, and project-only installation files created for the test.
2. For projects eligible for a template, add a portable copy under `src/harness/projects/templates/` and update the template catalog. Apply the [template acceptance standard](template-acceptance.md) for portability, the original source archive, the source and layout section in `AGENTS.md`, and checks on a copy. For projects exempt from template delivery, including SAEBase, GeneReasoning, and SpatialPheno, record the same test and acceptance evidence and skip this copy and catalog update.
3. Once acceptance and the template are verified, delete the downloaded checkout, extracted copies, setup backups, recovery archives, test logs, and trial-only historical runs. The template carries its original source ZIP, revision, and checksum. Record useful run evidence with the workflow it supports in the template. Preserve existing user checkouts, their established bindings, and shared resources. On a verification failure or external blocker, keep the working state and original package for repair or resumption.

Keep workspace `data/` in place during handoff, including data downloaded for a particular project. When a bounded precheck already proves a workflow, keep the command, expected result, and relevant resource requirements in the template. Preserve historical outputs only when a user needs those outputs to reproduce a result or exercise a reader. Record a local result separately while an item remains open or when the user explicitly asks to keep it.

Report each project after the batch with the independently verified outcome, template path, and completed cleanup. For incomplete projects, report the gap, attempts, next action, and exact blocker. Report a focused goal as achieved after fresh acceptance passes for every project in its confirmed scope.

## Test project uninstallation

Use this procedure when the requested outcome is removal of an installation. Follow [Project uninstallation](../../maintain-project/references/uninstallation.md) for the operation and ownership rules.

1. Choose the authorized existing checkout or a disposable project installation. From outside the target, save the pre-test registry, binding and connection state, inventory the files and their ownership evidence, and preserve the minimum source or restore evidence needed for the assessment. Include both a project-only resource and a retained resource when the existing installation provides them. Keep the evaluator's inventory and acceptance answers outside the agent's normal search locations until it finishes. If the agent read them, record that fact separately from the verified cleanup.
2. Start a new independent agent with a clean context. Give only a natural, short uninstall request and the target identifier. When the authorized request includes disposal of a trial's files, say so in that sentence. Wait for the agent to finish without sending the inventory or completion answers.
3. Compare actual paths and registration state against the starting inventory. Require removal of project-only artifacts and respect for retained files, bindings, and neighboring projects. A successful report alone does not pass. Test residual paths directly. If a repeat is needed, use a fresh agent and a comparable installation or continue the verified partial removal. Never recreate large resources solely for a second trial when the existing baseline can validate the remaining cleanup.

## Test sequential uninstall with a template choice

Use this goal when the user selects template delivery per project. Work in the user’s order. Give each fresh agent a short request containing the project identifier and either **add to templates** or **do not add to templates**. Keep the evaluator inventory and expected paths outside the request. A user-approved delivery may rely on bounded acceptance evidence. Carry the verified runtime scope into the template documentation.

Verify each project before dispatching the next. For an add, check the catalog, the template's original source ZIP and provenance, portable entry points, and the evidence that supports the requested acceptance. For a skip, verify that the trial created no template or catalog entry. Preserve any approved template that already existed before the test. For either choice, verify the registration is gone and the project's exclusive checkout, environment, caches, build files, experimental outputs, and acceptance or recovery copies are absent outside its template and workspace `data/`. Check that shared resources and other bindings still resolve.

If a check fails, locate the owning instruction or implementation, repair the reusable rule within scope, and have a fresh agent finish or retest the failed case from the available state. Delete evaluator material for a completed trial outside its template and workspace `data/`; give the user the final results in the handoff.

After the last project that uses a batch workspace finishes, reopen its shared files. Remove obsolete goal notes, source lists, manifests, evidence indexes, and empty work directories kept during earlier items. Check that retained entries serve another active goal or a reusable documented workflow. Then remove the evaluator's temporary batch plan.
