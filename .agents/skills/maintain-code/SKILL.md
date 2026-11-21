---
name: maintain-code
description: Review and maintain the selected code and its upstream/downstream, determine whether the core functionality meets the target from the real-use scene, position, repair and rescale as mandated, and confirm that the official access points will be able to recreate the results and clean up the temporary documents.
---

# Review and maintenance code around core uses

## Purpose

The system reads the existing code, understands the responsibilities of the document, the overall use of the catalogue and the upstream/downstream relationship, determines the adequacy of the achievement through the actual use of the scene, and decides to retain the existing realized or to supplement, streamline and organize the code with specific benefits.

The method of implementation is streamlined, with a clear and stable basis of judgement, which provides a direction for smart assistants to proactively investigate and solve problems and reduces the burden of human decision-making.

## Scope

Enter the target source code, the current task, as well as the structure charts, notes, instructions and existing tests, as required. Read the target items using standard files and search tools to test the operational environment in which the project is used.

The actual modification, testing and external operation uses the user ' s mandate for the current task and the working rules of the target project.

## Central path check and project restoration

ResearchHarness unified the maintenance of document paths, directory and naming. The assistant performing the research project uses read-only ResearchHarness and its verification portals to restore the public entry point, logic and results of the target project within the permitted range. When it is considered that the error or the rule is too strict, the inspection order, rules, path, reversible evidence and impact are included in the human-oriented report and continue to be independently completed.

## Working with humanity

When there is sufficient information, you can directly advance the investigation and the mandated maintenance. When there is a disagreement about the goal that will change the direction of the work, you can use the specific use to explain your understanding and obtain the required judgement from the user.

The assistant is responsible for identifying the fact of the code, determining whether it has been achieved adequately and selecting a proportionate method of modification, and for completing the connection between the call and the use of the result.

When the choice depends on the user’s research intent, use experience or input preferences, the specific circumstances, viable options, practical implications and recommendations are provided. For example, when the function is left dependent on the future use of the research, or when the programme changes the meaning of the research, the resource input, and the main mode of use, the specific differences in the user’s judgement will need to be made clear.

When larger adjustments to functional value or use are involved, a representative result is presented as early as possible, allowing users to judge whether it is helping to work. Examples, a set of cross-references or modifications to use can be used; new calculations and external operations follow the current mandate. User feedback is applied to the basis of the follow-up review, indicating how the direction of work is adjusted accordingly.

The findings of the review provide the basis for implementation, and the current mandate will be followed in practice. The user will complete the investigation and deliver the specific programme only when requesting the review and recommendation; the user will continue to complete the scope of the investigation, judgement, modification and clearance when the user has authorized maintenance.

`report_before_fix` Default is `true`.Before you start repairing, describe the deviations between the actual results and the core uses, the identified reasons and the proposed modifications, and then continue the mandated work. When new substantive deviations are detected, the description is updated before the next round of changes. `report_before_fix=false` Or "direct repair" before closing off.

## Relationship to scientific project preparation

`maintain-project` is responsible for the complete maintenance of the missing items, from the normal entrance to the components, configurations and products. When cross-component maintenance identifies duplication of duties, behavioural conflicts or functional gaps, this skill determines the location of the merger and the differences that need to be retained on the basis of a genuine call. `maintain-project` Implements the approved changes within the same maintenance, organizing a partial review of the relevant conduct and a review of the entire service chain.

## Relationship to the maintenance of assets on demand

`maintain-optional` provides guidance on how independent scripts, tests, project files and external documents in research projects are generated, validated, used and updated for any form of organization with corresponding responsibilities.

- **Tests.** Core functional examination provides enforceable evidence for the review. This skill determines the normal use scene, the results to be seen, and how current realizations and candidate changes should be compared. `maintain-optional` Directs the preparation, operation and maintenance of the inspection. When a real failure is detected, it is confirmed by the same check and repaired under the conditions approved for implementation, then the official return entrance will be accessed with a case-by-case access of continuing value.
- **Independent script.** This skill determines that the script is suitable for continued independent use, access to formal processes or removal along with the actual operator, input and delivery results. `maintain-optional` Guides how to achieve access, process the product and connect the user.
- **External document.** This skills-based judgement project provides guidance on practical functionality, affected callers, and the value of access or replacement through external content. `maintain-optional` Guidance on trial, source recording, updating, adaptation and formal access.
- **Temporary work on projects.** When you review a one-time script or document, you decide the long-term drop point according to the actual use. `tests/`,Manually. `scripts/`,Scientific calculations `tasks/`,Open Parameters `conf/`,Other achievement of the corresponding responsibilities module. Following the original call and document and moving to the public entry point, the temporary tasks were cleared after the handover was completed.
- **Project document.** The current description provides clues about the intended use and access, and reviews the cross-checking of these clues with the actual use.

## Reconciliation of document attribution and duplication of responsibilities

When organizing, moving or accepting the document layout of a scientific project, run `rh projects project check <project-root>` before changes are made and before delivery. Processes the returned violation and the catalogue review item in `directory_reviews`. The exit status `0` indicates that the mandatory machine rules have been passed, and `1` indicates that the violation or inspection has failed; the catalogue pile must still be inspected in accordance with actual duties.

The machine inspects the path, hierarchy, file type and rereadable component identifier. The real call is then used to check the functions that should be shared within the project and the behaviour that needs to be verified separately.

In scientific research, it's open. API,Command entry, distribution and common running codes in the final directory `base/`.Tables of actual data processing, modelling and research tasks, respectively `datasets/`,`models/`,`tasks/`,Formal Configuration to `conf/`.Project-wide maintenance to check each of the four code directories and in-service `scripts/`,`tests/`.Checks with existing commands and tests for actual landings; merge duplicates and keep the actual entry. 15 The grouping of a direct file. Check the package map with the existing import when adjusting the physical path and verify it along the public entry point of the project.

When organizing a file layout or judgement, the input, output, default, failure and side effects are compared with the actual caller and use the scene. The review gives the existing document or symbol, the specific duties that are repeated, the differences that need to be retained, the recommended location responsible and the person who moved. The name or location change requires checking the effect of normal commands, import, configuration, test findings and results read. The read-only scheme should indicate the entry and the judgement that can verify these effects.

When the existing result generation code is consolidated, the same complete archive is read at the original entry after validation, and the new output is written in a separate location and compared to the original output. Checks the presentation of the machine fields, values, filenames and reader-oriented. When it is agreed that the original output will be maintained and the content can be generated over time, the document contents will be compared on a case-by-case basis.

### Overregulated directory of files or subdirectories

When you maintain a directory, you start to check all subordinate directories on a layer-by-level basis, and again perform the same check on the newly created subdirectories in the sorting. Separate direct files and direct subdirectories. `datasets/` and `models/` The whole project is covered by old, unremoved checks. `src/` And an identifiable root level. Python Cache, generate products, third-party content, and an archive with an independent format are processed at their respective borders. When a specific skill specifies the layout of a catalogue, the directory is processed according to a specific purpose and continues to check the directory below which the project organizes itself.

The self-organized directory of the project directly contains**More than 15 File**At this point, check the use, actual caller, input output and common steps of the same layer. If multiple parallel functions occupy the document, are not yet centralized or can form a clear functional group by the actual function, then sort it out within the maintenance scope. First, the same function and reusable enable the actual module to be consolidated into the actual responsibility. The files that still need to be maintained independently enter the named subdirectories according to their true purpose and minimize the number of direct files at each level. [Migration and Merge Functions](references/move-and-merge.md) Select the consolidation approach based on the actual call relationship and apply to maintaining cross-documentation of the behaviour of the various entry points.

Actual reliance on decision consolidation and grouping. The number of direct files per directory at `base/`, `tasks/`, `scripts/`, `tests/` and the identifiable old source root levels is up to 15.

When the direct subdirectories exceed 15, check the use, caller, common code and differences by group. Repeat the focus to the responsible module, group members who share a responsibility by real family or workflow, and review the current access and results. Members with their own real responsibilities can retain them and justify them. If only one general directory or a whole move is added, continue to process the actual responsibilities.

This section also applies to running examples and studies of duplicate scripts. Checks that the same operation is generated by equipment, component selection or parameter extraction values and is included in the mouth. The same portion of the actual behaviour and input output is centralized, and the difference is expressed in meaningful parameters or famous formulations. The open access that needs to be retained calls that achievement and maintains the respective default values and visible results. The original baseline resource and its fixed discovery structure are retained to actually read the protocol.

The replica scripts still provided by the project cover formal functions, from scripts to actual reading, construction, training or rating statements. Code duties are set by root component directories, scripts are manually called and parameters are organized. In the absence of official running resources, the source splits, compatible access and independently checked actions continue to be completed; the delivery indicates evidence of the source position and the actual operation of the code.

## Check project documents against parameters

When you are running, check the configuration, environment and list that is in effect at the time. When the actual document, code and results differ, indicate the circumstances and effects, and update the realization, description and relevant entry as the restoration range is approved; the historical report is kept in accordance with the facts at the time.

The open parameters are implemented by `maintain-conf`. The functional review determines whether the parameters control useful behaviour, check the effects of omission, apparent extraction and old formulations on the actual consumer, and use the normal access check as authorized.

The project uses the configuration prefixes corresponding to the file structure to implement the naming agreement as a stand-alone quick check. The parameter attribution is determined by the actual configuration file and the corresponding realization position, and the task-specific field is checked for entry to the task prefix. When the project has a clear file or registration relationship for the subtask in the configuration, the prefixing of the same relationship is followed. The common key is determined on the basis of the actual common entry. The file, current key and expected attribution are reported and stored at the project's own test entry, e.g. `tests/test_conf.py`. The review of the configuration name and path is performed as authorized. The configuration navigation and the main text level is checked by the actual file tree. Under the sub-section of the directory, the parameters for which the document is responsible are found. The quick check should detect the missing small section, the wrong parent, source address, or the parameters of the wrong chapter. The parameter behaviour and document are checked by the actual consumer.

The configuration path is an independent audit entry. From the real entry to load and verify the source code, the path to the root of the item in which the source code is located is removed from the first two levels of the configuration. `conf/` Could not close temporary folder: %s `conf/` The next top two-tier directory, with only one file for each configuration branch, can be loaded separately from the physical entry to verify the name segment of the deeper responsibility. Distinguishing between the source code for the definition and the caller for the same configuration. Check the output actual file, the source code and the expected configuration. The configuration must be checked for new, modified and deployed. `doc/conf.md` Automatically synchronized according to the actual file. Document link correctly and parameter prefix correctly are the result of other checks, respectively.

## Check for product naming and reading

Checks the generation, continuation and reading of the results with the same name rule. The standard directory of genuine components and operations is extrapolated, and a fixed file name is used for the same function. Checks whether the summary and list are duplicated to keep the running address and follow it directly to the normal consumer. Paths can be derived by using the fixed rule, by including the same rules as those used for reading, and by recording the identity, configuration, status and scientific source of the list. Validation of the actual reading by removing or changing the address field in the aggregation, and then checking whether the old writing point has been cleaned up with the change.

## Core principles

**When the use is fully satisfied, it is recognized that the completion, retention and reduction of the subsequent burden are effective results..**

The changes suggest who will be affected in what circumstances, what improvements are expected, and the relationship between the proceeds and the costs of implementation and maintenance. They can be based on actual observations or on the path and consequences that can be clearly extrapolated from current implementation.

The replacement or deletion of a copy of the work is used to demonstrate that the act is being maintained, and the need for the change is determined by its actual use and specific benefits. The conclusions of the review and its basis are used as a starting point for follow-up; the new basis and its impact on the original judgement are presented in the context of the re-examination.

The test results provide the basis for the decision to change. The core functional gap is identified by testing the results available at the normal entrance or by being completed with permission.

The expected results are defined according to the purpose of the mission. The structure chart, notes and source code are used to understand duties and collaborative relationships; the actual results are used to judge the performance of functions.

The functional trade-off is based on actual use, call relationships and known conditions of occurrence. When the use is determined, it includes the assurance on which the current caller relies and the scene of the identified failure; and before the trial deletes, identify who uses the step and whether it has a responsible location. The test deletes, together with these grounds, support the deletion decision, and check that responsibility is moved with the merger to the actual responsible entry.

The same set of portable core functional tests supports three types of judgement:

- Runs the current code directly and finds the core result missing, which complements it.
- Temporary removal of candidate codes to run again to see if core results are compromised and to provide a basis for streamlining judgement.
- The functions are organized by moving or combining the code to re-run and to observe whether the same function continues to be performed.

Regular inspections are focused on key locations, and the results of the reuse are subsequently called upon.

The principles describe the basis for the functional trade-off and the operational memorandum preserves specific practices.

## Reading and Implementation

Starts with the user-selected object, selects the review mode by a single file or a whole directory. When interpreting to humans, the background and basis are based on the information required for this conclusion and decision.

### Single File

The documents and directories are used to explain the input, output, and actual impact; reading and testing advance around the core uses of the document.

### Full Directory

First understand what the directories do together, then go into the relevant documents by using them as a whole:

1. **Determination of overall use.** The directory contains several functions, distinguishing between the main work process and the support capacity for common use. Each process is described in terms of the need for use, the actual entry and the end result, and then explains how they use the common service catalogue as a whole.
2. **Trace the links between the directories.** Identify which external directories provide input, call this feature or continue to use the results, describing the actual entry point, information transmission and segregation of duties.
3. **Checks the complete usage process.** From the actual entry point to the preservation of the results, reading and subsequent use, determine whether the links are complete, the information is consistent, and whether normal completion and actual failures can be followed up. Focus is on the intersection: what is actually handed over in the first step, what is required in the next step, and whether the next step has the practical conditions to complete the operation.
4. **Evaluate the whole organization.** Determines whether the necessary work is accountable, duplicates the same function, and whether the various parts serve the current overall purpose. First form a holistic judgement, repositioning requires the retention, filling, access, consolidation or unloading of the actual impact. The change proposal prioritizes the problem of blocking the complete use. The directory moves, modular splitting and public programming are based on confusion, duplication of maintenance or use difficulties.

### Auxiliary structure information and functional trade-offs

Reference ExtractStructure(`extract-structure`)The generated structure information document, including the overall description of the directory, the document collaboration diagram, the sub-directorial relationship and the location of the source, helps to understand the links between the whole, the choice of the reading portal and the tracing directory. The information is used as an optional input, records its actual origin and coverage, and verifies key relationships based on the current source code. When information is missing or outdated, direct reading of the corresponding source code continues to be reviewed; the configurations, resources or other documents not listed in the chart are included in the reading according to their actual purpose. This skill review method is implemented independently, and the structure chart is generated or updated in accordance with this mandate.

When codes are found that have not yet been used for existing processes, they continue to identify the actual use, the mode of call (including the indirect call after configuration or registration), the location where responsibility exists, and the impact of access and unloading, respectively. Clear recommendations are given to these candidates for “retention and access” or “offload” as to who would benefit from a specific job, what additional connections are needed, what capacity would be lost, and the relationship between the benefits and the cost of maintenance. “No caller” is used as the basis for the survey to support judgement with actual use and impact.

It is recommended that access be retained, indicating specific access points, sources of input, end-users and required changes; and, when offloading, indicate the extent of the clean-up of proprietary realizations, correlation statements, configurations and displays.

Priority is given to existing tests that check the core results, supplementing the minimum input with the expected results, as required. Implementation is done through the normal entrance, with the official reading of the results confirming content and downstream use. The test input is based on the information required to make this change decision.

Amends the responsible module within the delegated authority. Completing, deleting, moving and combining the simultaneous processing of actual affected calls, access, configurations and tests.

## Invalid old entry after moving or merging

Use the same input to validate the results and subsequent reading through the reserved open access. Path compliance calls the central layout and test checks, and source evidence and Python behaviour examples to indicate that the access is still operational.

## Reporting to humans

If you are involved in a directory pile, the response indicates the results of the re-routing of the paths and the re-routing of the direct number of files and subdirectories, the actual consolidation or grouping of the affected entry. If the threshold for the review of the subdirectories is still exceeded, the remaining gaps or the basis for the use of the independent members of each group are indicated.

The findings of the review, the actual changes and their use are presented first, and then the background and basis for understanding the conclusions are provided. The content and length are organized according to existing user perceptions, the results and the matters to be decided upon.

The completed maintenance describes the outcome and the actual impact; when sufficient, the reasons for the support for the reservation. Matters requiring the user’s decision indicate the specific choice, the proceeds, the costs, the scope and the helper’s recommendations. The problem explanation includes the circumstances, the actual results and the implications for the follow-up, and clearly distinguishes between real environmental observations, isolated sample replication and source code extrapolation.

Full job sheets, source locations and investigative processes are stored as needed in the workbook and are supported by corresponding links. Evidence that affects current conclusions or decisions is described in the body of the document.

For the first time, when a complex subject is presented or a complete report is requested by the user, the following structure can be used, which can be carried out on the basis of a practical understanding:

- **Examines what the object does and where:** gives the path, the functionality and the normal use scene, explaining the input, the main operation and the available results.
- **How relevant documents and folders fit:** describes the necessary internal composition and external collaboration for a serial call, information transfer, preservation, reading and subsequent use; a table is used when relationships are higher.
- **Review findings and practical implications:** Evaluate the adequacy of the overall use and interface and explain the specific gaps, conditions, impact and basis.
- **Modifications, proceeds and scope:** describes the behaviour, specific proceeds, implementation and maintenance costs to be changed, and identifies the matters that have been addressed and that need to be determined by the user.

When referring to chapters, functions, rules or programmes, use a name that describes the content. It is forbidden to identify anything with a numbered letter or number. Official names and machine interfaces, where they exist, use the original name when an accurate reference is required. Background helps users to understand the results, judge their actual value and base their current decisions.

## Continuous resolution of problems when identified

1. **achieves the results before the restoration.** selects the real-use scene and identifies the results that users need to obtain and the public entry point.
2. **Repair and re-detection.** When additional evidence is required, use the minimum representational scene and use comparable conditions, depending on the time available and the impact of the results. `tmp/` This is a special catalogue. If there is still a deviation, continue to locate and repair new evidence.
3. **Confirms that the public entry point is available.** will require long-term implementation, testing, or input into the official location of the access project.
4. **Clear this temporary file.** Confirms that the public entry point can be reproduced independently, and records the access, conditions and results that can be reproduced, and deletes the temporary script, input copy, output and work directory that was created.

## Read the instructions on demand

- [Identification of core functions](references/core-purpose.md):Description of how core uses are determined in conjunction with the structure chart, notes and source code; applicable when reading the target file and selecting the normal use scenario.
- [Identification and completion of core functions](references/identify-gaps.md):Save examples of operations that have been achieved by regular access to identify the missing core results and complement them; applicable to the determination of whether core functions are completed and position gaps.
- [Identification of non-deleting functions](references/identify-extras.md):Saves the temporary removal of candidate steps, compares core results and decides on streamlined operational methods; applies to the determination of whether the inspection or other steps need to be retained.
- [Migration and Merge Functions](references/move-and-merge.md):Saves the operating methods for moving, combining and reusing core tests based on actual duties; applies to cross-documentation functions.
- [Design discussion](references/design.md):Core purpose of documentation skills, issues raised by humans and established principles of determination; applicable for continuing discussion, revision and testing of skills.

## Local data

When there is a continuous process, a short `execution.md` is maintained in the same job catalogue, describing the context and objectives, documenting key actions and judgements over time, and following up with a summary of the actual results and subsequent recommendations, with links to the results.

Interim input, copy of work and running results from this skill are kept in itself as required `results/<run ID>/` , in the task directory `log_updates.jsonl` Record the time frame, the relative path within the skill, the brief content and the actual source.

## Item-by-line

Check the public selection and document entries from the public entry point and user work. Check the duplicate options, the values covered by the default policy, the fixed or open values, and the relationship between tasks, subtasks and products under the same objective.

Examines whether the document is located along the actual directory and is used independently. Checks whether each reference is submitted for the purpose, scope of application, main content and example of the target information, and checks whether the body provides a key basis for judgement from the reader ' s point of view.
