# ResearchHarness — job description for smart assistant

## Purpose

This document describes the entire catalogue of ResearchHarness, when smart assistants are required to maintain ResearchHarness, and the seven management principles that must be followed in maintaining the document, and to guide the corresponding operations document to specific tasks.

## Scope

Use the maintenance process described below when the scientific project is involved in the maintenance of ResearchHarness itself.

## ResearchHarness for a scientific project

Read and write in accordance with this mandate and operational identity. Registers are used to locate projects, binds to the selection of in-house resources, and shares skill switches for synchronized skills.

Each project should be capable of being installed, configured and operated independently. The installation steps, dependence, data selection and public commands are provided by the project.

When a common methodology is developed, you can identify the problems, the conditions under which it is established and how the same facts are obtained in different organizational forms. Skills are written in terms of the applicable circumstances, the basis to be checked, the method of judgement and the conditions for its completion. A unique catalogue of the project, the order and the agreement are kept in the description of the corresponding project.

### Overall and dedicated maintenance of the project

**Access to an unknown project, inspection or maintenance of the entire scientific project, first using [maintain-project](.agents/skills/maintain-project/SKILL.md).** This skill follows the physical entrance to check the first-level catalogue and cross-component process, defaults on specific maintenance to the applicable parts, and then checks on the modified project as a whole.

**Direct use of tailor-made skills for individual maintenance.** Datasets, models and missions are used separately `maintain-dataset`,`maintain-model` and `maintain-task`.Cross-component movement and shared operational capability utilization `maintain-base`,Open Parameter Use `maintain-conf`,Single run configuration and experimental operation use `maintain-experiment`,Use of stand-alone scripts, tests, component documents and external files `maintain-optional`.Maintenance of the entire project by `maintain-project` Assignment of specific tasks according to these responsibilities.

A single-time project is available at `maintain-tmp`. The access project can be dependent on the ResearchHarness to bind the interpreter and install the project statement. Hugging Face download location is maintained at `huggingface-maintain` and data preprocessing and reusable caches are attributed to the corresponding data.

## 1. Main Directory of ResearchHarness

- `src/agent/` Saves maintenance of ResearchHarness's own job description.
- `.agents/skills/` Preservation of skills for any scientific project.
- `src/harness/` provides access to shared skills, tied in-house resources, review of structural results and independent tools.
- `src/project/` Saves the central identity by project, shares the set-up, works experience, binds the in-house resources and structural results.
- `.workspace/` Keeps central project registration, operational status and development products.
- `tests/` Saves a needs-based regression test for a central command and tool.
- `pyproject.toml` Configure packages and development tools.

## 2. When can we modify ResearchHarness?

The general scientific mission is carried out within the corresponding project.

**It is currently in the development phase. ResearchHarness Users must clearly approve the scope of the change before the source, configuration, specifications or directory structure is available.** Central Harness Reconstruct the implementation to the extent explicitly approved by the user.

The scientific project code reviews, plans and collaborates with the project’s GitHub process. ResearchHarness uses current user-authorized and operational identities for its own operation.

When the user requests the addition of a Harness feature, the user is asked to specify the following: the gap between current capabilities and needs, how the new functionality will be used in the operation, and which documents are expected to be added or modified; and if the functional meaning or effect needs to be clarified, the user is asked to specify the objectives.

When the user requests that Harness be scaled down, the context of the use of the document or mechanism to be deleted, the actual caller and the removal effect are identified, and the specific option to be reserved, merged or deleted is given to the user. The reservation and consolidation should be based on the actual use, and the deletion is aimed at removing the approved mechanism directly.

## 3. Seven upholding principles

### Purpose-driven principles

Each function, rule and document must serve a clear and realistic need. The description of this need should be specific and clear, providing an indication of the issues to be addressed and their practical implications.

### 2. Principles of human understanding

All designs must give humans a clear understanding of what they mean, what they play and what they use. The term should be clearly explained, contextd and practical, with human understanding given priority.

### 3. Principle of certainty of conduct

The operation of the smart assistant requires that the trigger be clearly defined, the person to be executed, the specific act and the expected outcome, so that the smart assistant can perform consistent operations according to the same rule.

### 4. Principle of partial binding

The rules should be placed in the modules and operational links where they are actually needed. The global constraint should be applied only to those rules that are truly applicable to the system as a whole; each specific constraint must accurately describe the tasks, objects and operations to which it applies.

### 5. Optional principles of certification

There is a need to look at whether the smart assistant can actually implement the expected behaviour, and the certification mechanism as a capacity to choose on demand. The ResearchHarness is currently in the development stage, with the **validation operation being disabled, with a specific check being performed at the specified range** at the user’s express request; the certification mechanism and process is being developed according to the user’s needs.

### 6. Streamlining principles

Functional and binding reservations are based on a clear and effective practical role.

### 7. Principles of writing, interpretation and dialogue

This principle applies to writing documents, explaining problems to and communicating with humanity, with a view to ensuring that human beings can understand what is written and said.

1. **Use a name to describe actual meaning.** When writing titles, naming or quoting chapters, functions, rules, schemes and other objects, use a name that explains the object or purpose, and lets the reader see the name to know what it means. It is prohibited to refer to anything with a numbered letter or number, and to package with a technical term that can be described directly. Such numbers and words do not themselves convey meaning, and the reader needs to find a different description to understand them. When using a common professional term, for the first time, it is used to indicate what it means in the current context, as required. When a proper reference is made to an official name, file path or machine interface, the original name is used.
2. **Use the full natural language.** Consistency of abbreviations and code expression is replaced by a full description that humans can understand directly.
3. **describes the concept and connection in a positive sentence.** describes directly the meaning, role, interrelationship and application of each concept, with the concept distinction and boundary statement in a positive sentence.
4. **Provides details on the basis of human needs.** Daily writing and communication is based on understanding of practical problems, uses and results; technical details and implementation boundaries are then developed when humans clearly request them.

#### Options for sharing information

Within the current mandate, the assistant is responsible for obtaining the facts, completing the engineering judgement and continuing the task, and humans provide, inter alia, the purpose, actual use of feedback and input preferences. When a choice requires new human intent or a trade-off judgement, the assistant describes the circumstances, viable options, practical implications and recommendations; and technical issues with significant implications explain the conditions and consequences.

**Select the content to be shared around the results of the mission.** Dialogue helps humans understand actual changes, address issues and make decisions. Regular implementation, necessary inspections and routine tailings are part of the process of completing the task, with a direct indication of the results obtained and their practical use.

**Direct delivery of documents for download and external review.** Humans need to download documents and provide directly the results that can be downloaded during external review or analysis, by default containing the main information and necessary instructions to complete the use. Individual documents can be delivered directly and multiple documents that need to be handed over together can be compressed packages; humans will be required to deliver in their specified format or content range.

## 4. Opening statements for all Harness documents

Each activity maintained by ResearchHarness Markdown, Python, configuration or other document should begin with a statement that:

- **Purpose and main function**: Why the document exists, what specific functions it provides, or what data it keeps.
- **Scope of application **: which tasks, modules or operations will read or modify it, as well as the subject subject, trigger conditions and operational boundary.

Markdown documents used to bind Harness have a uniform positive sentence and, in particular, in the section “Purpose and main function” and “Scope of application”, should be precise in describing roles, functions, conditions of application and factual circumstances.

Markdown uses these two same-name subsections; Python can use the top-module document string; the format supporting the note can use the file header annotated. Machine files such as JSON maintain a legitimate syntax with the current data format, describe a programme that is readable in a compatible manner and allow the user to decide on the specific form.

When a restricted Markdown uses the Markdown link to quote another Harness binding document, the reference should be accompanied by a statement of the " Purpose and main function " of the referenced document and the " Scope of application " , consistent with the statement at the beginning of the target document. Each link should serve the actual reading needs of the current task.

Read and maintain a description of the current mandate. This relates to the description of the current mandate document, which is amended in conjunction with the corresponding maintenance; questions affecting the understanding, execution or mandate decision are presented in the context of the specific impact.

## 5. Select the special document according to the current task

- [Project shared skills and in-house operations](src/harness/projects/README.md)Description of how to synchronize skills, choose data and Python and manage the results of the structure, applicable to the in-house access of the selected project.
- [Catalogue of research projects and documentation functions](src/harness/projects/LAYOUT.md)Provides for catalog attribution, enabler conditions and call relationships, applicable to projects that establish, organize or expand the layout.
- [Smart assistant day job.](src/agent/AGENT_FLOW.md)Description of the procedures, skills and instructions for maintaining the warehouse on the basis of its true use, applicable ResearchHarness Self-development.
- [Public function in central workspaces](src/harness/core/README.md)Description of the location of the machine ' s catalogue, atom writing and product records, applicable to the maintenance of central shared realization.
- [Project access and in-house resources](src/harness/core/PROJECT.md)Description of the first-level layout of the parent area and the project, data, Python and the positioning of structural results, applicable to arrange parent directories, in-house registration, resource allocation and results reading.
- [Transfer & Relief](src/harness/utils/transfer/README.md)Description of the parameters and results for downloading, uploading, checking and selective decompression, applicable to tasks that clearly require the processing of documents or maintenance tools.

## 6. Work boundary at the current stage of development

The actual function is based on a specific program and project entry. Validation, model downloads, scientific operation and real data transfer are performed in accordance with the user's specified requirements and delegated range. The project's source code, default scientific configuration, precheck, running records and experimental products are returned to the project. Centrally binds the preservation machine resource selection, and structural results reviewer's decision on a specific ExtraScructure page version.

The documentation path, directory, naming and experimental product path rules for research projects are governed by the central inspection of ResearchHarness. The overall acceptance is checked `rh projects project check` through `base/`, `datasets/`, `models/`, `tasks/`, `conf/`, physical components and tree-wide paths, and the main function is validated by the public entry point. The assistant performing the specific scientific project task visits ResearchHarness in a read-only manner, using a central read-only inspection, to repair the target project within the mandate.

## 7. Workspace of the machine and attribution of the product

`.workspace/` is located in the ResearchHarness warehouse, which is used to preserve the configuration, operation and development of the machine.

The modular product attribution in this section applies to the operation and development products generated by the central management program `.workspace/`. The resource binding and structural results of a single project are kept at `src/project/<project>/resources.json` and `src/project/<project>/structure/`. The experimental operating products of a scientific project (including reference templates) are integrated into the respective project contents `experiment/`. Project skills companion files and local products are stored in their respective skill directories under section 8.

Contents Press `src/` Three main subjects `agent/`,`harness/`,`project/` Organisation, mirroring the actual Level 2 directory. The product enters the corresponding Level 3 directory; the Level 3 directory uses the source file name (deleted) `.py`)or a more deep source code directory name.:

```text
src/harness/utils/probe.py         → .workspace/harness/utils/probe/
```

The project path of `central.py` is `.workspace/harness/core/central/`. The installation-dependent process file is `.workspace/harness/projects/install/`, which is recovered when the installation is withdrawn. `cli.py` Distribution commands are distributed and the product is placed in the actual execution module.

Use the name of each separate file or complete package `<Content or use>_<Project, time or other identifier>`,For example: `project_roots.json`,`environment_saebase-20261103T075412Z.json`,`site_saebase/`.The product is centrally stored in the three-tier catalogue of the attribution module. The complete web page, virtual environment, historical snapshots, etc., is a famous product package; the original file name and content are maintained in the package. The compound package is the module of the organization's package, and the internal call source is described in the log according to the actual sources known to you.

Each of the three-tier directories in use has a short `log_updates.jsonl`. Every time a product is added, received or updated, additional time (time zone), relative path, brief content and source source; the program is recorded by the appropriate entry, the smart assistant manually by the smart assistant. The package can be recorded once by the members; the log entry object is limited to the product file and package. The source is filled in on a practical basis and the source to be confirmed is written “unknown”.

The old information belonging to the confirmation is placed at `.workspace/tmp/<purpose>_<id>/`, where the same log and the original path description is kept. The migration retains the content, permissions and historical identity of the original document; the old path in the original record is kept as a historical fact. The structure results are kept on a specific page, source version, analytical scope and review decision.

## 8. Independence and products of project skills

When adding or modifying project skills in `.agents/skills/<skill-name>/`, use the folder as the complete delivery unit:

- The **companion file is kept in the skills.** Use instructions, scripts, references, templates, styles and other running resources are kept in this skills directory; internal references are used in relative locations that can be moved with the entire folder.
- **Specialization of skills required for operation to be kept within skills.** Skills-specific workflow descriptions, process realization, templates and mapping resources are derived from documents in this skills directory. ResearchHarness The public inspection is on duty. `src/harness/core/` Centralize maintenance. Skills can be used to call their public read-only commands.
- **Operators and operating conditions are clear.** Skills include user-specified input, operator, target service and necessary running environment tools in their own statements. Read target items, standard tools such as calling Git, or access to target services such as GitHub, which are handled according to specific mandate; these operations are described separately from skills outside the citation directory or customize achievement.
- **Local products remain in the interior.** Implementation results, release preparation copies, interim documents, caches, and logs are stored in a generic subdirectories in this skill directory.
- The **release is aimed at internal copies.** distribution skills actually copy a user-selected directory or file into their own directory, and then prepare the copy for submission, package and upload. The original release object is read-only and the document content remains the same as the file collection; Git initialization, construction, packing and writing of the required supporting documents are done within the skills. The release copy is saved by a separate file, the catalogue of work and the writing location point to the skills; the initial content of the copy is consistent with the user-selected range, and the adjustments to the release content are processed with the user ' s express authorization.
- **You can continue after moving the whole thing..** The program locates the matching file and product according to the skill ' s own location, and the project path and release target is clearly assigned to the task.


## Public access and support functions

| File or directory | Current responsibilities |
| --- | --- |
| `src/harness/cli.py` | Distribution of project and stand-alone tool orders. |
| `src/harness/central.py`、`src/harness/core/workspace.py` | Positioning the machine project, atoms are recorded in the central record and the product is registered. |
| `src/harness/projects/` | Synchronize shared skills to manage in-house data, Python and structural results. |
| `src/harness/utils/` | Process transfer, depression, process environment observation and snapshot comparison. |
| `tests/` | Check the actual order as required and maintain it with the reservation function. |
