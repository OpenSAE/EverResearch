---
name: maintain-skill
description: Test whether EverResearch can independently maintain supplied research projects. Run routine adoption by default, improve EverResearch against a confirmed goal, or follow an explicit request to record or analyze a conversation or run a skills exam.
---

## Runtime compatibility

The repository skills are synchronized with EverResearch source. This distribution's launcher uses the published EverResearch 0.3.1 wheel. For source workflows that require the `.everresearch/` setup or a source-only command, use the CLI from the corresponding [EverResearch source checkout](https://github.com/OpenSAE/EverResearch/commit/9b036cb2109788a8545724a03c313502d255d187). Use the project's existing maintenance entry point when working with the published runtime.

# Assessment and maintenance skills

## Run the EverResearch CLI

Use Python 3.11, 3.12, or 3.13 to run `scripts/rh.py` from the current skill,
followed by the arguments after `rh`. For example, pass `projects project check <project-path>` to check a
project. Use `${CLAUDE_SKILL_DIR}` in Claude Code or Cowork and the staged skill
directory in Claude web.

The launcher uses the packaged runtime when available. GitHub marketplace
installs download the pinned wheel once and verify its checksum before use.
The launcher creates a private environment and may fetch Python dependencies.
With no Python execution available, review the files you can
access and tell the user which automated checks you could not run.

For a separate terminal installation, the official PyPI package is
`ever-research` from OpenSAE. The PyPI project named `researchharness` is
maintained separately.

## Purpose and main function

Test EverResearch on real research projects, turn recurring failures into reusable improvements, and verify the outcome through an independent agent. Also record and review maintenance conversations or run a skills exam when requested.

## Scope of application

Use for projects supplied directly or identified by articles, links, or other source material. An invocation with projects and no special emphasis starts routine independent adoption. Explicit requests to record, analyze, or run an exam use their respective workflows below.

## Test maintenance on supplied projects

With a short invocation and supplied projects, start the routine test directly and work through the projects in the supplied order.

1. Locate the project's original repository or release. For a paper, follow the authors' code or artifact link. Download a new project into a directory created for the test. If the user supplies an existing checkout as the target, use that directory. Before any project edits, save an original package containing the starting state and record where it came from.
2. Start a new subagent with no previous conversation. Set its working directory to the project directory from the previous step. Give it exactly two lines, `maintain-project` and the project name. The subagent uses the normal EverResearch workflow and reports what it changed, which public commands it ran, and where the results are. Wait for it to finish before reviewing the work.
3. Check the project files and the evidence from the public commands. If a repair is needed, diagnose the cause and use the same project directory for follow-up rounds. For final acceptance after repairs, extract the saved original package into a fresh directory and put a new subagent there. This tests whether it can complete the work from the same starting files without inheriting the earlier repairs.
4. After acceptance, remove any EverResearch connection created for the test. Add and verify a template copy for eligible projects. Then remove the files created solely for the test. Preserve existing user checkouts and shared resources.

**Template exemption.** SAEBase, GeneReasoning, SpatialPheno, and any other project the user exempts use the same working-directory rules and acceptance checks. Keep their test evidence and skip adding them to the template catalog.

Use [Template acceptance](references/template-acceptance.md) when adding or reviewing a template. It defines the portable maintenance files, original source archive, and standard origin and layout section in `AGENTS.md`.

If the user gives a specific issue, emphasis, or requirement, use the material to propose a plain-language outcome that applies to comparable projects. Explain what users should be able to do and how the result will be verified. Confirm the goal and any changes to the routine acceptance scope with the user before starting the independent tests.

Follow [Independent project testing and goal-driven repair](references/goal-testing.md) to resolve sources, prepare original project packages, run short-prompt tests, verify acceptance, and deliver templates. Use the same repair loop when a routine project fails or a confirmed goal remains unmet. Keep goal and test evidence in local `goal/<goal-name>/` directories under the skill's writable state path. The goal-testing guide defines the evidence to keep.

For an uninstall goal, use the [uninstall test procedure](references/goal-testing.md#test-project-uninstallation) to preserve evidence, give a fresh agent a short uninstall request, and verify actual cleanup and retained resources.

When the user specifies which projects should become templates, use [sequential uninstall with a template choice](references/goal-testing.md#test-sequential-uninstall-with-a-template-choice).

## Record or analyze a project conversation

Use the source skill directory for local work in a checkout. In an installed release, `rh guide skill-state maintain-skill` gives the local directory for `agent_log/` and newly generated exams. Read the exam rule and references from the skill itself.

When invoked with **记录**, create or update the Markdown log for the selected project conversation in this skill's `agent_log/` directory. Save the user's exact requests in order, a factual summary of what the assistant did for each request, and the paths of new, modified, moved, or generated files. Recording is complete when the file has been written and read back.

When invoked with **分析**, open the selected conversation log and audit how the assistant handled file placement, naming, and subsequent reading and writing. Send the user the findings with the current path, correct path, applicable rule, cause, and evidence. Analysis stops at the findings until the user gives a correction, accepts a finding, or otherwise directs a skill change. When either command is invoked on its own, use the current project and conversation if they uniquely identify the intended log.

When the user responds, use only the findings and corrections they authorize as the basis for changes. Improve the relevant skill rules so they cover other projects and comparable cases. A repair may change one skill file or several skills and their companion files. By default, show the changed locations and what each change is expected to catch after editing and before the independent test. The user can turn off this preview with `preview_after_edit=false`. A preview is a review point. If the user has already authorized the test, continue after showing it unless they have asked to review first.

Follow [Conversation logs and independent review](references/conversation-review.md) for the exact log format, audit output, feedback handling, and test handoff. The reference applies to the 记录 and 分析 entry points and to follow-up skill changes based on those logs.

## Evaluate maintenance plans with project questions

Use [Project maintenance exam rules](exam/exam_rule.md) to design and review plan-only questions based on each project's real capabilities. The rules define coverage, candidate-visible prompts, and evidence for scoring. Apply them when testing whether a subagent can independently route a maintenance request and propose changes through read-only inspection.

## Run Options

The default is `report_before_fix` `true`. You can write in this request `report_before_fix=false` or state "direct fix" to inform you before the restoration is closed. On-line, before being modified, a brief description of the actual result that deviates from the user ' s purpose, the identified cause and how it is to be repaired. When new material deviations are detected, an update is provided before the next round of changes. After the notification, the approved work continues, only if the programme involves a new mandate or requires a user ' s trade-off.

## Watch the real use and judge the results

1. Read the target skills and the material that it actually uses, and write out the detectable success terms in combination with the user’s intent. Selective access covers the actual target for this purpose, specifying where the user enters, provides what, can eventually see or continues to use. Select the range of retrospect based on the impact of the known failure on this result.
2. Prefer real requests, run records, and deliverables. Preserve a reviewable baseline before restoration and record versions, project state, environment, and observed outcomes. Preserve the original project packages for routine and focused project tests and follow the shared independent test sequence.
3. Check the content of the delivery and downstream use on a successful basis. The successful loading of skills, the exit of scripts and the existence of the product will only indicate that the corresponding steps have been completed. The determination of whether or not the purpose of the delivery is achieved is based on the actual ability of the user to use the delivery results. Recording evidence comes from the real environment, the isolated recurrence or the static analysis; the latter two are used for positioning issues, and the true environment conclusions are based on actual observations.

## Keep each responsibility in its owning file

Before adding or changing guidance, find the file that already owns the operation. Identify its trigger, inputs, decisions, actions, and completion evidence. Keep project coordination in `maintain-project`, specialist procedure in the skill responsible for it, and detailed supporting material in that skill's companion files. Conversation records, feedback, and independent test design belong to `maintain-skill`.

When guidance is repeated, reconcile its requirements in the owning file and replace other copies with links that explain when to use it. If a change crosses several responsibilities, update each owner and their call points together. Give every file a distinct purpose. Preserve supported entry points and evidence requirements when moving instructions. Review neighboring skills for conflicting rules after a move.

## Positioning, repairing and retracing causes

1. Determines whether the skills were discovered and used, whether the then-directed guidance enabled the assistant to make the necessary judgement, whether the actual access and tools were capable of being consumed, and whether the results were consumed downstream.
2. When there is a gap in skills detection or operational guidance, amend the corresponding description, step, or associated resources. When there is a gap in public capacity, EverResearch revises the corresponding central accomplishment. Target project entry, script or task capability is not sufficient, and restores it as it is authorized. Project Implementation Assistant maintains a read-only reading of EverResearch and identifies the rules, pathways, and effects of the mid-pointing in the reporting when the central error is detected. Environmental issues are treated as if they are actually dependent on and configured.
3. After each restoration, start a new independent testing assistant. Compare the delivery and downstream use with the baseline. For an agreed goal, run follow-up repairs on the current test checkout and perform final acceptance from the original package as specified in the goal workflow.

## Confirm a repair in a fresh and a used checkout

When feedback spans setup, tooling, and project behavior, retain the reported versions and one reproducible observation for each issue. Check first use from a fresh clone, then repeat the normal entry point in a checkout with representative generated files. Verify which runtime the entry point actually invokes and how a downstream command reads its outputs. Keep the issue list and expected results in the evaluator's local evidence. Apply common fixes in the owning command or skill and project-specific fixes in the project.

## By an independent test assistant

The evaluator selects the target, retains the benchmark, and reviews the results. For project file placement and naming evaluations, start a clean-context subagent with exactly these two lines:

```text
maintain-project
<ProjectName>
```

Fill in only the actual project name, for example the uniquely registered name. Select an environment in which that name resolves to the intended project. Supply no file paths, log contents, findings, proposed fixes, expected outcomes, or acceptance answers. Give the subagent a neutral task label and do not inherit conversation history or send hints. Establish project access and permissions in the execution environment before dispatch. For other skill evaluations, use the same clean-context procedure with the selected skill name and its target identifier. The subagent independently discovers, repairs within its authorization, and reports from the ordinary project entry points.

Upon receipt of the response, the evaluators independently examine the actual documents, operational evidence and subsequent use to determine whether the report is reasonable and the results met the standard. Pre-test evidence and the necessary raw samples are retained to avoid the situation that has been processed to cover the original gap. Python can check the path, product and reading back; the assistant is right to judge and continue to process on the basis of this independent operation and delivery.

During an independent repair test, the evaluator only waits for completion or the timeout. Apply the [waiting and timeout procedure](references/goal-testing.md#wait-for-the-independent-agent) with an initial limit of 60 minutes unless the user sets another limit.

For a blind test of default onboarding, use the user's exact ordinary request in a clean
agent session with the target checkout as its working directory and the current skills
available through normal discovery. Keep the baseline, intended checks, and hints outside
the agent's prompt. Verify the public entry and read back reusable results. Observe how the
agent selects short executions during setup and explains any longer runs. See the
[short-run guidance](../maintain-project/references/coordination.md#keep-setup-runs-short).

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

The whole project structure assessment starts with and is independently reruned from `rh projects project check --json`. The five top-level directories and actual components, and the number of documents, are accepted and accepted. Independently, the main order determines the true realization document, checking the actual handling of the coordination code and the `base/` at `datasets/`, `models/`, `tasks/`, respectively. Checks whether or not the attribution and functional duplication of `scripts/`, `tests/` are handled. Only when actual evidence is read in a way that is compatible with the old entry, original functionality and official results will the project be passed. The structural evaluation also examines the existing disk tree, the current reading of the entry and the navigation given to the user.

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
