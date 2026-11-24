---
name: maintain-skill
description: Record project conversations, analyze file placement and naming from recorded work, and improve or independently evaluate the skills responsible.
---

# Assessment and maintenance skills

## Purpose

When the result is found to be biased, the cause is located along the execution process, automatically repaired and re-evaluated within the current authorization, and adjusted on the basis of new evidence until the key scene meets the target or there is a clear impediment.

## Scope

The input includes the target skills and the project or environment in which they are used, as well as the user's description of the purpose, true request or operational record. First, you fill the scene with the existing material; then you ask the user to be clear when the target skills, the use environment or the expected results are still uncertain and change the conclusions.

## Record or analyze a project conversation

When invoked with **记录**, create or update the Markdown log for the selected project conversation in this skill's `agent_log/` directory. Save the user's exact requests in order, a factual summary of what the assistant did for each request, and the paths of new, modified, moved, or generated files. Recording is complete when the file has been written and read back.

When invoked with **分析**, open the selected conversation log and audit how the assistant handled file placement, naming, and subsequent reading and writing. Send the user the findings with the current path, correct path, applicable rule, cause, and evidence. Analysis stops at the findings until the user gives a correction, accepts a finding, or otherwise directs a skill change. When either command is invoked on its own, use the current project and conversation if they uniquely identify the intended log.

When the user responds, use only the findings and corrections they authorize as the basis for changes. Improve the relevant skill rules so they cover other projects and comparable cases. A repair may change one skill file or several skills and their companion files. By default, show the changed locations and what each change is expected to catch after editing and before the independent test. The user can turn off this preview with `preview_after_edit=false`. A preview is a review point. If the user has already authorized the test, continue after showing it unless they have asked to review first.

Follow [Conversation logs and independent review](references/conversation-review.md) for the exact log format, audit output, feedback handling, and test handoff. The reference applies to the 记录 and 分析 entry points and to follow-up skill changes based on those logs.

## Run Options

The default is `report_before_fix` `true`. You can write in this request `report_before_fix=false` or state "direct fix" to inform you before the restoration is closed. On-line, before being modified, a brief description of the actual result that deviates from the user ' s purpose, the identified cause and how it is to be repaired. When new material deviations are detected, an update is provided before the next round of changes. After the notification, the approved work continues, only if the programme involves a new mandate or requires a user ' s trade-off.

## Watch the real use and judge the results

1. Read the target skills and the material that it actually uses, and write out the detectable success terms in combination with the user’s intent. Selective access covers the actual target for this purpose, specifying where the user enters, provides what, can eventually see or continues to use. Select the range of retrospect based on the impact of the known failure on this result.
2. Prefer to existing real-life requests, run records and deliverables. Preserve reviewable benchmarks before restoration and initiate the initial test as "by an independent testing assistant". Record the skill versions, object status, environment, operational and delivery.
3. Check the content of the delivery and downstream use on a successful basis. The successful loading of skills, the exit of scripts and the existence of the product will only indicate that the corresponding steps have been completed. The determination of whether or not the purpose of the delivery is achieved is based on the actual ability of the user to use the delivery results. Recording evidence comes from the real environment, the isolated recurrence or the static analysis; the latter two are used for positioning issues, and the true environment conclusions are based on actual observations.

## Keep each responsibility in its owning file

Before adding or changing guidance, find the file that already owns the operation. Identify its trigger, inputs, decisions, actions, and completion evidence. Keep project coordination in `maintain-project`, specialist procedure in the skill responsible for it, and detailed supporting material in that skill's companion files. Conversation records, feedback, and independent test design belong to `maintain-skill`.

When guidance is repeated, reconcile its requirements in the owning file and replace other copies with links that explain when to use it. If a change crosses several responsibilities, update each owner and their call points together. Give every file a distinct purpose. Preserve supported entry points and evidence requirements when moving instructions. Review neighboring skills for conflicting rules after a move.

## Positioning, repairing and retracing causes

1. Determines whether the skills were discovered and used, whether the then-directed guidance enabled the assistant to make the necessary judgement, whether the actual access and tools were capable of being consumed, and whether the results were consumed downstream.
2. When there is a gap in skills detection or operational guidance, amend the corresponding description, step, or associated resources. When there is a gap in public capacity, ResearchHarness revises the corresponding central accomplishment. Target project entry, script or task capability is not sufficient, and restores it as it is authorized. Project Implementation Assistant maintains a read-only reading of ResearchHarness and identifies the rules, pathways, and effects of the mid-pointing in the reporting when the central error is detected. Environmental issues are treated as if they are actually dependent on and configured.
3. After each restoration, a new testing assistant is initiated to re-evaluate with the same skill, same object and comparable initial state. Compare the delivery and downstream use of the initial and secondary measurements.

## By an independent test assistant

The evaluator selects the target, retains the benchmark, and reviews the results. For project file placement and naming evaluations, start a clean-context subagent with exactly these two lines:

```text
maintain-project
<ProjectName>
```

Fill in only the actual project name, for example the uniquely registered name. Select an environment in which that name resolves to the intended project. Supply no file paths, log contents, findings, proposed fixes, expected outcomes, or acceptance answers. Give the subagent a neutral task label and do not inherit conversation history or send hints. Establish project access and permissions in the execution environment before dispatch. For other skill evaluations, use the same clean-context procedure with the selected skill name and its target identifier. The subagent independently discovers, repairs within its authorization, and reports from the ordinary project entry points.

Upon receipt of the response, the evaluators independently examine the actual documents, operational evidence and subsequent use to determine whether the report is reasonable and the results met the standard. Pre-test evidence and the necessary raw samples are retained to avoid the situation that has been processed to cover the original gap. Python can check the path, product and reading back; the assistant is right to judge and continue to process on the basis of this independent operation and delivery.

## Independent detection and repair of file placement

When testing is authorized, start the clean-context subagent with only the two-line project assignment above. Keep the conversation log and every evaluation detail outside the assignment. Let the subagent independently inspect and repair the project within the authorization available in its environment.

The maintenance assistant starts from the physical tree and public commands. Trace representative producers and consumers for each discovered category. Repair the responsible writer and affected readers, migrate existing files with their identities intact, and verify that a new invocation follows the repaired path. Work through all affected instances, including older runs still read by a current command. Leave actively written files in place until their producer has finished. Report each finding with its original path, intended path, producer, reader, and verification evidence. The evaluator reviews the actual changes and uses a fresh independent subagent for a repeat check after any further repair.

Select coverage from the project's actual capabilities:

| Case | Evidence required |
| --- | --- |
| Reusable preparation and alternative splits | A named asset preserves source provenance and distinct input identities. The writer and representative readers use the revised location. |
| Default, named, repeated and batch execution | All segments of each generated path satisfy the naming rule. Exercise a descriptive name and invalid names containing dates or opaque identifiers, including a suffix under a valid parent. Verify that rejection precedes directory creation, and repeated execution preserves earlier evidence. |
| Training and downstream analysis | A retained analysis can rerun independently, traces the source checkpoint or data, and lists the actual outputs. The producer and manifest agree on report and artifact ownership. |
| Temporary tools and research-specific scripts | Disposable output is bounded to its working area, installed dependencies resolve outside the project, and reusable commands can be found under the owning research area. |
| Existing runs and checker conflicts | A normal reader retrieves the same retained result after migration. Record central checker output separately from the independent check for descriptive names and file ownership. Report unresolved differences with exact paths and rules. |

At a review-only stage, show the revised skill locations and explain which evidence each rule would require. Start the independent test when the user authorizes it or when the current mandate already includes it. Apply any user-requested review pause before launch.

## Receiving and Inspection File Naming and Reading

The entire project document assesses the independent check `doc/environment/README.md` and the document index link. Based on the actual installation entry, the operating configuration and the description of the existing running record check, it is determined that the preparation conditions, light authentication methods and the actual operating environment can be found. The item does not pass when the environment page is missing, only the title, the index is not linked or the description does not match the actual entry.

When the task requires that products be organized according to fixed rules, the evaluator determines independently, before the start, the rules to be followed and the observations to be observed from the real entry and the operational entry, and records the rereadable existing product. Checks the actual writing, running and reading at the normal entry. When the physical summary record of the project has been located in the member, changes the address in the isolated sample, confirming that the consumer can still find the real product according to the agreed identification and path.

The whole project structure assessment starts with and is independently reruned from `rh projects project check`. The five top-level directories and actual components, and the number of documents, are accepted and accepted. Independently, the main order determines the true realization document, checking the actual handling of the coordination code and the `base/` at `datasets/`, `models/`, `tasks/`, respectively. Checks whether or not the attribution and functional duplication of `scripts/`, `tests/` are handled. Only when actual evidence is read in a way that is compatible with the old entry, original functionality and official results will the project be passed. The structural evaluation also examines the existing disk tree, the current reading of the entry and the navigation given to the user.

When evaluating difficult directory placement, rerun the layout check and verify each group's intended destination and retained dependencies. The project maintenance record should identify where each group went and how it was verified.

When the task requires classification and integration, the evaluator selects the real approximation function from the previous level of the same directory and independently examines the changed family, membership, co-achievement and members' normal entry. When moving, changing or philosophies only, continue to check whether there are still multiple realizations or independent activations of the same function. Readers' navigation and results tree receive and receive from their actual duties.

When assessing the documentation in the catalogue, the number of direct files and direct subdirectories before and after the applicable catalogue is independently recalculated, the root `datasets/` and `models/` sub-tree waivers are checked to check whether the implementer has found the self-defined in-depth catalogue and whether the applicable special layout is specified. For more than 15 direct files or direct subdirectories, there are directories that can be integrated and assigned, and the common steps are centralized, downgraded to the actual purpose, and the affected entry points are available. The direct file is still too limited, or when there is an accumulation of sub-directories and there is no basis for their respective independent responsibilities, it is not processed.

Checks at the receiving and inspection mission level the research capability of a submission and the ability of a cross-mission call to determine the attribution of each group according to the actual call. When the acceptance experiment tree is used to determine the attribution of each group of files from the actual generation and reading access, check the corresponding research input for the first level of path and confirm the reading of the new and existing results. When a duplicate prefix is found with a real family, the actual path of the receiving family and multiple members is checked.

## Independent evaluation and generalization of rules

- Steps, memos, examples, and handling opinions are designed in different organizational ways. Technical details of the case-specific and trifling steps are not allowed into the skills or central rules. Checking the new rules remains in place under different project names, organizational forms and results formats; the facts of the case remain in independent evaluation records or corresponding project information.
- The evaluators independently maintain the baseline and acceptance evidence and determine the results as required by the user. The test layout reruns the tree-wide and independent tests and finds the true results' attribution and official reading back. Compares the number of performances covered, distinguishing between the movement of historical assets and the actual operation through a formal laboratory inspection. The project for which the examiner is missing uses the actual producer, the outcome document and the reader to locate the missing. The retrofit uses a comparable state to record the new evidence for the front and current rounds, respectively.

## Temporary running and closing

- Priority reuse items have already been entered. `tmp/` This is the next dedicated directory. The script calls the public entry point and formally realizes a project-dependent, sustainable resource.
- Site access projects that prevent the failure of the same purpose in the long term `tests/`.Operation tool access required for repeated manual use `scripts/`.Functional access as part of the project 's official task `tasks/`.The provisional catalogue is cleared using the results of tests already in place or a representative validation as required to confirm that the required results can be repeated with official access, formal configuration and sustainable resources only.
- The final report describes the representative scene, whether the purpose was achieved, actual evidence before and after the restoration, changed location, and the clean-up or formal setting of interim information. Where obstacles remain, indicate which results are lacking and what conditions are required.
