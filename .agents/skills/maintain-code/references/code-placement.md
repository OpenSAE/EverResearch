# Place and consolidate project code

## Purpose and main function

Place and consolidate project code.

## Scope of application

Use when moving files, merging entry points, or resolving directory and dependency findings.

## Relationship to scientific project preparation

`maintain-project` is responsible for the complete maintenance of the missing items, from the normal entrance to the components, configurations and products. When cross-component maintenance identifies duplication of duties, behavioural conflicts or functional gaps, the skills determine the location of the merger and the differences that need to be retained on the basis of a genuine call. `maintain-project` Implements the approved changes within the same maintenance, organizing a partial review of the behaviour and then checking the entire use chain.

## Relationship to the maintenance of assets on demand

`maintain-optional` provides guidance on how independent scripts, tests, project files and external documents in scientific research projects are generated, validated, used and updated for any form of organization with corresponding responsibilities.

- ** Tests. ** Core functional examination provides enforceable evidence for the review. This skill determines the normal use scene, the results to be seen, and how current realization and candidate changes should be compared. `maintain-optional` directs the preparation, operation and maintenance of the inspection. When a real failure is detected, it is confirmed by the same check and repaired under the conditions approved for implementation, then the formal return entry will be accessed with a case-by-case access of continuing value.
- ** Independent script. ** This skill determines that the script is suitable for continued independent use, access to the official process or removal, along with the actual operator, input and delivery results. `maintain-optional` Guides how to achieve access, process the product and connect the user.
- ** External document. ** This skills-based judgement project provides guidance on practical functionality, affected callers, and the value of access or replacement through external content. `maintain-optional` Guidance on trial, source recording, updating, adaptation and formal access.
- **Temporary work on projects.** When you review a one-time script or document, you decide the long-term drop point according to the actual use. `tests/`,Manually. `scripts/`,Scientific calculations `tasks/`,Open Parameters `conf/`,Other achievement of the corresponding responsibilities module. Following the original call and document and moving to the public entry point, the temporary tasks were cleared after the handover was completed.
- ** Project document. ** The current description provides clues about the intended use and access, and reviews the cross-checking of these clues with the actual use.

## Reconciliation of document attribution and duplication of responsibilities

When organizing, moving or accepting the document layout of a scientific project, run `rh projects project check <project-root>` before changes are made and before delivery. Processes the returned violation and the catalogue review item in `directory_reviews`. The exit status `0` indicates that the mandatory machine rules have been passed, and `1` indicates that the violation or inspection has failed; the catalogue pile must still be inspected in accordance with actual duties.

The machine inspects the path, hierarchy, file type and rereadable component identifier. The real call is then used to check the functions that should be shared within the project and the behaviour that needs to be verified separately.

In scientific research, it's open. API,Command entry, distribution and common running codes in the final directory `base/`.Tables of actual data processing, modelling and scientific missions, respectively `datasets/`,`models/`,`tasks/`,Formal Configuration to `conf/`.Project-wide maintenance to check each of the four code directories and in-service `scripts/`,`tests/`.Checks with existing commands and tests for actual landings; merge duplicates and keep the actual entry. 15 The grouping of a direct file. Check the package map with the existing import when adjusting the physical path and verify it along the public entry point of the project.

When organizing a file layout or judgement, the input, output, default, failure and side effects are compared with the actual caller and use the scene. The review gives the existing document or symbol, the specific duties that are repeated, the differences that need to be retained, the recommended location responsible and the person who moved. The name or location change requires checking the effect of normal commands, import, configuration, test findings and results read. The read-only scheme should indicate the entry and the judgement that can verify these effects.

When the existing result generation code is consolidated, the same complete archive is read at the original entry after validation, and the new output is written in a separate location and the original output is compared to the original. Checks the presentation of the machine fields, values, filenames and reader-oriented. When it is agreed that the original output will be maintained and the content can be generated over time, the document content will be compared on a case-by-case basis.

### Overregulated directory of files or subdirectories

When you maintain a directory, you will examine all the subdirectories from level to level and again the new subdirectories that are being created. Separate direct documents and direct subdirectories will be counted. The root levels `datasets/` and `models/` and their future generations exemption numerical rules will continue to check duties, duplicate realization and real access. The whole project will cover old, undisplaced `src/` and identifiable root Python packages. Cachelization, creation products, third-party content and separate format files will be processed at their respective borders.

The self-organized directory of the project directly contains**More than 15 File**At this point, check the use, actual caller, input output and common steps of the same layer. If multiple parallel functions occupy the document, are not yet centralized or can form a clear functional group by the actual function, then sort it out within the maintenance scope. First, the same function and reusable enable the actual module to be consolidated into the actual responsibility. The files that still need to be maintained independently enter the named subdirectories according to their true purpose and minimize the number of direct files at each level. [Migration and Merge Functions](move-and-merge.md) Select the consolidation approach based on the actual call relationship and apply to maintaining cross-documentation of the behaviour of the various entry points.

Actual reliance on decision consolidation and grouping. The number of direct files per directory at `base/`, `tasks/`, `scripts/`, `tests/` and the identifiable old source root levels is up to 15.

When the direct subdirectories exceed 15, check the use, caller, common code and differences by group. Repeat the focus to the responsible module, group members who share a responsibility by real family or workflow, and review the current access and results. Members with their own real responsibilities can retain them and justify them. If only one general directory or a whole move is added, continue to process the actual responsibilities.

This section also applies to running examples and studies of duplicate scripts. Checks that the same operation is generated by equipment, component selection or parameter extraction values and is included in the mouth. The same portion of the actual behaviour and input output is centralized, and the difference is expressed in meaningful parameters or famous formulations. The open access that needs to be retained calls that achievement and maintains the respective default values and visible results. The original baseline resource and its fixed discovery structure are retained to actually read the protocol.

The replica scripts still provided by the project cover formal functions, from scripts to actual reading, construction, training or rating statements. Code duties are set by root component catalogues, scripts are manually called and parameters are organized. In the absence of official running resources, the source splits, compatible access and independently checked actions continue to be completed; the delivery indicates evidence of the source position and the actual operation of the code.

## Check project documents against parameters

When you are running, check the configuration, environment and list that is in effect at the time. When the actual document, code and results differ, indicate the circumstances and effects, and update the realization, description and relevant entry as the restoration range is approved; the historical report is kept in accordance with the facts at the time.

The open parameters are implemented by `maintain-conf`. The functional review determines whether the parameters control useful behaviour, check the effects of omission, apparent extraction and old formulations on the actual consumer, and use the normal access check as authorized.

The project uses the configuration prefix corresponding to the file structure to implement the naming agreement as a stand-alone fast-track check. The task-specific field is attributed to the actual configuration file and the corresponding realization position, and checks whether the task-specific field enters the task prefix. When the project has a clear file or registration relationship for the subtask in the configuration, the prefixing of the same relationship is followed. The common key is determined on the basis of the actual common entry. The file, current key and expected attribution are reported and stored at the project's own test entry, e.g. `tests/test_conf.py`. The review of the configuration name and path is performed as authorized. The configuration navigation and the main text level are checked by the actual file tree. Under the sub-section of the directory, the parameters for which the document is responsible are traced. The quick-check should be able to detect the missing small sections, the wrong parent, source address or the parameters of the wrong chapter. The parameter behaviour and document are checked along with the actual consumer.

The configuration path is an independent audit entry. From the real entry to load and verify the source code, the path to the root of the item in which the source code is located is removed from the first two levels of the configuration. `conf/` Could not close temporary folder: %s `conf/` The next top two-tier directory, with only one file for each configuration branch, can be loaded separately from the physical entry to verify the name segment of the deeper responsibility. Distinguishing between the source code for the definition and the caller for the same configuration. Check the output actual file, the source code and the expected configuration. The configuration must be checked for new, modified and deployed. `doc/conf.md` Automatically synchronized according to the actual file. Document link correctly and parameter prefix correctly are the result of other checks, respectively.

## Check for product naming and reading

Checks the generation, continuation and reading of the results with the same name rule. The standard directory of genuine components and operations is extrapolated with a fixed file name for the same function. Checks whether the aggregate and list are duplicated to keep the running address and follow it directly to the normal consumer. The path is followed by the fixed rule, and the same rule is written and shared with the read-in, the list records the identity, configuration, status and scientific source. Checks the actual readout by removing or changing the address field in the aggregate, and then check whether the old writing point has been cleaned with the change.

## Reading and Implementation

Starts with the user-selected object, selects the review mode by a single file or a whole directory. When interpreting to humans, the background and basis are based on the information required for this conclusion and decision.

### Single File

The documents and directories are used to explain the input, output, and actual impact; reading and testing advance around the core uses of the document.

### Full Directory

First understand what the catalogues do together, then go into the relevant documents by using them as a whole:

1. **Determination of overall use.** The directory contains several functions, distinguishing between the main work process and the support capacity for common use. Each process is described in terms of the need for use, the actual entry and the end result, and then explains how they use the common service catalogue as a whole..
2. ** Trace the links between the directories. ** Identify which external directories provide input, call this feature or continue to use the results, describing the physical access, information transmission and segregation of duties.
3. ** Checks the complete usage process. ** From the physical access to the preservation of the results, reading and subsequent use, determine whether the links are complete, the information is consistent, and whether normal completion and actual failures can be followed up. Focus is on the intersection: what is actually handed over in the first step, what is required in the next step, and whether the next step has the practical conditions to complete the operation.
4. ** Evaluate the whole organization. ** Determines whether the necessary work is accountable, duplicates the same function, and whether the various parts serve the current overall purpose. First form a holistic judgement, repositioning requires the retention, filling, access, consolidation or unloading of the actual impact. The change proposal prioritizes the problem of blocking the complete use. The directory moves, modular splitting and public programming are based on confusion, duplication of maintenance or use difficulties.

### Auxiliary structure information and functional trade-offs

Reference ExtractStructure(`extract-structure`)The generated structure information document, including the overall description of the directory, the document collaboration diagram, the sub-directorial relationship and the location of the source, helps to understand the links between the whole, the choice of the reading portal and the tracing directory. The information is used as an optional input, records its actual origin and coverage, and verifies key relationships based on the current source code. When information is missing or outdated, direct reading of the corresponding source code continues to be reviewed; the configurations, resources or other documents not listed in the chart are included in the reading according to their actual purpose. This skill review method is implemented independently, and the structure chart is generated or updated in accordance with this mandate..

When codes are found that have not yet been used for existing processes, they continue to identify the actual use, the mode of call (including the indirect call after configuration or registration), the location where responsibility exists, and the impact of access and unloading, respectively. Clear recommendations are given to these candidates for “retention and access” or “offload” as to who would benefit from a specific job, what additional connections are needed, what capacity would be lost, and the relationship between the benefits and the cost of maintenance. “No caller” is used as the basis for the survey to support judgement with actual use and impact.

It is recommended that access be retained, indicating specific access points, sources of input, end-users and required changes; and, when offloading, indicate the extent of the clean-up of proprietary realizations, correlation statements, configurations and displays.

Priority is given to existing tests that check the core results, supplementing the minimum input with the expected results, as required. Implementation is done through the normal entrance, with the official reading of the results confirming content and downstream use. The test input is based on the information required to make this change decision.

Amends the responsible module within the delegated authority. Completing, deleting, moving and combining the simultaneous processing of actual affected calls, access, configurations and tests.

## Expire old entry after moving or merging

Use the same input to validate the results and subsequent reading through the reserved open access. Path compliance calls the central layout and test checks, and source evidence and Python behaviour examples to indicate that the access is still operational.

## Local data

When there is a continuous process, a short `execution.md` is maintained in the same job catalogue, describing the context and objectives, documenting key actions and judgements over time, and following up with a summary of the actual results and subsequent recommendations, with links to the results.

Interim input, copy of work and running results from this skill are kept in itself as required `results/<run ID>/` , in the task directory `log_updates.jsonl` Record the time frame, the relative path within the skill, the brief content and the actual source..
