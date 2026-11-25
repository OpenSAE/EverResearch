# Review code and report findings

## Purpose and main function

Review code and report findings.

## Scope of application

Use for understanding callers, reviewing code behavior, and explaining or verifying a repair.

## Central path check and project restoration

ResearchHarness unified the maintenance of document path, directory attribution and naming. The assistant performing the scientific research project uses read-only ResearchHarness and its verification portals to restore the public entry point, logic and results of the target project to the extent permitted. When error is considered or the rules are too strict, the inspection orders, rules, pathways, reversible evidence and effects are included in the human-oriented report and the independently completed project is maintained.

## Check dependencies of core components

Core code in `base/`, `models/`, `tasks/`, and `datasets/` can use other core components, the Python standard library, and installed dependencies. Keep project code and file access within these four directories. This restriction covers direct and indirect imports, execution, and reads of project paths such as `conf/`, `experiment/`, `assets/`, `scripts/`, `tests/`, and `tmp/`, as well as other external files. Callers may read configuration or data and pass the resulting values to core components.

`experiment/` stores run records and results. Core components may write their output there. Scripts and tests may read those results for analysis, review, and testing.

With Python 3.11 or later, run `python -B <skill-directory>/check_dependencies.py <project-root>`. Locate the script beside this skill's `SKILL.md`. Run the check when reviewing or editing code and repeat it after fixing dependencies. It scans statically resolvable Python references in the four core directories and reports code, scripts, notebooks, and common compiled files under `experiment/`. Exit status `0` indicates that the scan found no violations. Status `1` indicates violations. Status `2` indicates invalid input, no core Python files to scan, or a read error.

1. Include the affected core components and their dependency chains. When starting from an optional directory, trace back to any core callers. For a project-wide review, cover all four core directories.
2. Follow imports, dynamic loading, script execution, and file access. Resolve the targets through configuration, registries, package mappings, and shared helpers. Verify paths determined at runtime and calls from other languages through the relevant public entry point. Review documentation links and output-only writes according to their purpose.
3. Record the original file and line, public entry point, full dependency chain, and resolved target. When a repair is authorized, preserve needed behavior in the responsible module and trace the entry point again after making the change. Keep unresolved targets or remaining violations open.

## Working with humanity

When there is sufficient information, you can directly advance the investigation and the mandated maintenance. When there is a disagreement about the goal that will change the direction of the work, you can use the specific use to explain your understanding and obtain the required judgement from the user.

The assistant is responsible for identifying the fact of the code, determining whether it has been achieved adequately and selecting a proportionate method of modification, and for completing the connection between the call and the use of the result.

When the choice depends on the user’s research intent, use experience or input preferences, the specific circumstances, viable options, practical implications and recommendations are provided. For example, when the function is left dependent on the future use of the research, or when the programme changes the meaning of the research, the resource input, and the main mode of use, the specific differences in the user’s judgement will need to be made clear.

When larger adjustments to functional value or use are involved, a representative result is presented as early as possible, allowing users to judge whether it is helping to work. Examples, a set of cross-references or modifications to use can be used; new calculations and external operations follow the current mandate. User feedback is applied to the basis of the follow-up review, indicating how the direction of work is adjusted accordingly.

The findings of the review provide the basis for implementation, and the current mandate will be followed in practice. The user will complete the investigation and deliver the specific programme only when requesting the review and recommendation; the user will continue to complete the scope of the investigation, judgement, modification and clearance when the user has authorized maintenance.

`report_before_fix` Default is `true`.Before you start repairing, outline the deviations between the actual results and the core use, the identified reasons and the proposed modifications, and then continue the mandated work. When new substantive deviations are detected, the description is updated before the next round of changes. `report_before_fix=false` Or "direct repair" before closing off..

## Core principles

**When the use is fully satisfied, it is recognized that the completion, retention and reduction of the subsequent burden are effective results..**

The changes suggest who will be affected in what circumstances, what improvements are expected, and the relationship between the proceeds and the costs of implementation and maintenance. They can be based on actual observations or on the path and consequences that can be clearly extrapolated from current implementation.

The replacement or deletion of a copy of the work is used to demonstrate that the act is being maintained, and the need for the change is determined by its actual use and specific benefits. The conclusions of the review and its basis are used as a starting point for follow-up; the new basis and its impact on the original judgement are presented in the context of the re-examination.

The test results provide the basis for the decision to change. The core functional gap is identified by testing the results available at the normal entrance or by being completed with permission.

The expected results are defined according to the purpose of the mission. The structure chart, notes and source code are used to understand duties and collaborative relationships; the actual results are used to judge the performance of functions.

Functional trade-offs are based on actual use, call relationships and known conditions of occurrence. The scope of use is determined by including the assurance on which the current caller relies and the observed failure scene; and by identifying who uses the step and whether it has a responsible location before the deletion is tested. The deletion results together with these grounds support the deletion decision and check that responsibility is moved with the merger to the actual responsible entry.

The same set of portable core functional tests supports three types of judgement:

- Runs the current code directly and finds the core result missing, which complements it.
- Temporary removal of candidate codes to run again to see if core results are compromised and to provide a basis for streamlining judgement.
- The functions are organized by moving or combining the code to re-run and to observe whether the same function continues to be performed.

Regular inspections are focused on key locations, and the results of the reuse are subsequently called upon.

The principles describe the basis for the functional trade-off and the operational memorandum preserves specific practices.

## Reporting to humans

If you are involved in a directory pile, the response indicates the results of the re-routing of the paths and the re-routing of the direct number of files and subdirectories, the actual consolidation or grouping of the affected entry. If the threshold for the review of the subdirectories is still exceeded, the remaining gaps or the basis for the use of the independent members of each group are indicated.

The findings of the review, the actual changes and their use are presented first, and then the background and basis for understanding the conclusions are provided. The content and length are organized according to existing user perceptions, the results and the matters to be decided upon.

The completed maintenance describes the outcome and the actual impact; when sufficient, the reasons for the support for the reservation. Matters requiring the user’s decision indicate the specific choice, the proceeds, the costs, the scope and the helper’s proposal. The problem explanation includes the circumstances, the actual results and the impact on the follow-up, and clearly distinguishes between real environmental observations, isolated sample replication and the source code extrapolation.

Full job sheets, source locations and investigative processes are stored as needed in the workbook and are supported by corresponding links. Evidence that affects current conclusions or decisions is described in the body of the document.

For the first time, when a complex subject is presented or a complete report is requested by the user, the following structure can be used, which can be carried out on the basis of a practical understanding:

- ** Examines what the object does and where: ** gives the path, the functionality and the normal use scene, explaining the input, the main operation and the available results.
- ** How relevant documents and folders fit: ** describes the necessary internal composition and external collaboration for a serial call, information transfer, preservation, reading and subsequent use; a table is used when relationships are higher.
- ** Review findings and practical implications: ** Evaluate the adequacy of the overall use and interface and explain the specific gaps, conditions, impact and basis.
- ** Modifications, proceeds and scope: ** describes the behaviour, specific proceeds, implementation and maintenance costs to be changed, and identifies the matters that have been addressed and that need to be determined by the user.

When referring to chapters, functions, rules or programmes, use a name that describes the content. It is forbidden to identify anything with a numbered letter or number. Official names and machine interfaces, where they exist, use the original name when they require an accurate reference. Background helps users to understand the results, judge their actual value and base their current decisions.

## Continuous resolution of problems when identified

1. ** achieves the results before the restoration. ** selects the real-use scene and identifies the results that users need to obtain and the public entry point.
2. **Repair and re-detection.** When additional evidence is required, use the minimum representational scene and use comparable conditions, depending on the time available and the impact of the results. `tmp/` This is a special catalogue. If there is still a deviation, continue to locate and repair new evidence..
3. ** Confirms that the public entry point is available. ** will require long-term implementation, testing, or input into the official location of the access project.
4. **Clear this temporary file.** Confirms that the public entry point can be reproduced independently, and records the access, conditions and results that can be reproduced, and deletes the temporary script, input copy, output and work directory that was created..

## Read the instructions on demand

- [Identification of core functions](core-purpose.md):Description of how core uses are determined in conjunction with the structure chart, notes and source code; applicable when reading the target file and selecting the normal use scenario.
- [Identification and completion of core functions](identify-gaps.md):Save examples of operations that have been achieved by regular access to identify the missing core results and complement them; applicable to the determination of whether core functions are completed and position gaps.
- [Identification of non-deleting functions](identify-extras.md):Saves the temporary removal of candidate steps, compares core results and decides on streamlined operational methods; applies to the determination of whether the inspection or other steps need to be retained.
- [Migration and Merge Functions](move-and-merge.md)Maintaining operating methods based on actual responsibilities migration, consolidation, handling cross-border reliance on core components and replicating core tests, applicable to cross-documentation functions and relying on infractions.
- [Design discussion](design.md):Core purpose of documentation skills, issues raised by humans and established principles of determination; applicable for continuing discussion, revision and testing of skills.

## Item-by-line

Check the public selection and document entries from the public entry point and user work. Check the duplicate options, the values covered by the default policy, the values that can be fixed or should be opened, and the relationship between tasks, subtasks and products under the same objective.

Examines whether the document is located along the actual directory and is used independently. Checks whether each reference is submitted for the purpose, scope of application, main content and example of the target information, and checks whether the body provides a key basis for judgement from the reader ' s point of view.
