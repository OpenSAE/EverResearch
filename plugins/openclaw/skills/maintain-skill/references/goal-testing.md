# Goal-driven repair and independent testing

## Purpose and main function

Use real failures to improve EverResearch so it can handle other projects and conditions that share their causes. Verify the improvement through the ordinary project entry points and a complete independent repair from the original state.

## Scope of application

Use this sequence for an abstract maintenance goal agreed by the human and assistant. The waiting and timeout procedure also applies to other independent repair tests started by `maintain-skill`.

## Preserve the goal and each original project

1. Write down the agreed outcome, the affected workflows, and the observations that would show the outcome was achieved. For each reported issue, record how it appeared and which other situations may share its cause. Use these facts to define what the same workflow should do when the project, environment, or inputs change.
2. Under `goal/<goal-name>/`, preserve a separate original package for every affected project before repair. Record its source, revision, initial state, and reproduction evidence. Retain the files and metadata needed to reproduce the starting state, including local material when it is part of the failure and may be stored there. Verify that the package can be extracted and keep it unchanged throughout testing. Save working checkouts and round evidence separately from the originals.
3. Use the goal to review and improve EverResearch before the first repair round. Trace each failure through skill selection, guidance, commands, environment selection, project entry points, and downstream use as applicable. Repair shared causes in their owning skills, templates, or implementation. Keep project-specific evidence in the goal records. Check how the revised behavior would handle comparable cases that were absent from the original report.

## Start the first repair round

1. Extract the original project package into an independent test location. Make the revised EverResearch available through its normal discovery and execution paths. Before dispatch, configure project registration, working location, permissions, and any other environment conditions the user would normally supply. If the test covers automatic resource setup, start with those resources absent.
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

When an issue remains, identify its cause and improve EverResearch. Start a new clean-context subagent with the same standard instruction on the current problem checkout so it can continue the repair. Apply the same waiting rule. Repeat until all known issues meet the goal and the applicable acceptance criteria on the working checkout.

## Accept the goal from the original package

After the continuation rounds pass, extract the untouched original package into a fresh test location. Use the final EverResearch revision and a new subagent with only the same standard instruction. **That same subagent must solve all the issues in one round from the original state with the same EverResearch revision.** A legitimate long-running task may resume under the timeout procedure in that same round. For a goal with several affected projects, complete this acceptance for each original package using the same final EverResearch revision.

If fresh acceptance exposes a remaining issue, return to the repair loop and repeat the original-package test with a fresh subagent after the next change. Report the goal as achieved only after original-package acceptance passes. The final report states the agreed goal, the shared causes repaired, the independent results and routine checks, and any blockers that prevented completion.
