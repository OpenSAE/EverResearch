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

1. After fresh acceptance, remove any temporary EverResearch registration and resource bindings created for the test. Preserve the accepted source and the evidence needed for handoff.
2. For projects eligible for a template, add a portable copy under `src/harness/projects/templates/` and update the template catalog. Apply the [template acceptance standard](template-acceptance.md) for portability, the original source archive, the source and layout section in `AGENTS.md`, and checks on a copy. For projects exempt from template delivery, including SAEBase, GeneReasoning, and SpatialPheno, record the same test and acceptance evidence and skip this copy and catalog update.
3. Once the acceptance evidence and any required template are verified, delete the downloaded checkout, extracted copies, temporary source archives, and other files created solely for that project test. Keep the delivered ZIP with the template and keep concise evidence, the upstream revision, and the archive checksum in the goal record. Preserve existing user checkouts, their established bindings, and any resources shared with other projects. On a verification failure or external blocker, keep the working state and original package for repair or resumption.

Report each project after the batch with the independently verified outcome, template path, and completed cleanup. For incomplete projects, report the gap, attempts, next action, and exact blocker. Report a focused goal as achieved after fresh acceptance passes for every project in its confirmed scope.
