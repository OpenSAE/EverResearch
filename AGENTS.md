# ResearchHarness — job description for smart assistant

## Purpose

This document describes the entire catalogue of ResearchHarness, when smart assistants are required to maintain ResearchHarness, and the seven management principles that must be followed in maintaining the document, and to guide the corresponding operations document to specific tasks.

## Choose the skill from the request

Before starting a task listed below, read and follow the linked skill. A request in ordinary language is enough to select it. The skill defines the workflow, required approvals, and completion checks. For a request with several actions, read the skills for the affected actions.

| When the user asks to… | Read first |
| --- | --- |
| Set up an unfamiliar project with EverResearch, check a whole project, or coordinate changes across several components | [`maintain-project`](.agents/skills/maintain-project/SKILL.md) |
| Change a shared CLI command, launcher, component wiring, resource selection, or result I/O | [`maintain-base`](.agents/skills/maintain-base/SKILL.md) |
| Add, change, or remove a dataset, loader, preprocessing, labels, or splits | [`maintain-dataset`](.agents/skills/maintain-dataset/SKILL.md) |
| Add, change, or remove a model, variant, initialization, or checkpoint loading | [`maintain-model`](.agents/skills/maintain-model/SKILL.md) |
| Add, change, or remove training, evaluation, inference, a metric, or an automatic precheck | [`maintain-task`](.agents/skills/maintain-task/SKILL.md) |
| Add, remove, or change a reusable configuration option, default, or preset | [`maintain-conf`](.agents/skills/maintain-conf/SKILL.md) |
| Run, resume, reproduce, or inspect an experiment using the available tasks and settings | [`maintain-experiment`](.agents/skills/maintain-experiment/SKILL.md) |
| Review, debug, or refactor code and trace the affected callers | [`maintain-code`](.agents/skills/maintain-code/SKILL.md) |
| Write a reusable helper or plot, add a regression test, or update docs or assets | [`maintain-optional`](.agents/skills/maintain-optional/SKILL.md) |
| Try an idea once or create a disposable script, plot, or note | [`maintain-tmp`](.agents/skills/maintain-tmp/SKILL.md) |
| Compare with GitHub, push, open a PR, publish a release or tag, or update a GitHub deployment | [`maintain-github`](.agents/skills/maintain-github/SKILL.md) |
| Get data or weights from Hugging Face, publish a Hub dataset, or check or update a Space | [`maintain-huggingface`](.agents/skills/maintain-huggingface/SKILL.md) |
| Save a lesson, decision, or research idea from the conversation as a reusable note | [`maintain-knowledge`](.agents/skills/maintain-knowledge/SKILL.md) |
| Test EverResearch on supplied projects, log or analyze maintenance decisions, or run a skills exam | [`maintain-skill`](.agents/skills/maintain-skill/SKILL.md) |
| Explain the structure of a paper or codebase, or build a diagram or interactive map | [`extract-structure`](.agents/skills/extract-structure/SKILL.md) |
| Check, submit, or update an EverResearch listing in an agent marketplace | Open the maintainer-only `.agents/skills/maintain-plugins/SKILL.md` when available in the local checkout. |

For an identified project, follow its own `AGENTS.md` and its current maintenance mode. For a single component, start with its skill. For a whole project, start with `maintain-project` and follow its handoffs.

## Scope

Use the maintenance process described below when the scientific project is involved in the maintenance of ResearchHarness itself.

## ResearchHarness for a scientific project

Read and write in accordance with the current mandate and operational status. Registers are used to locate projects, bind to the selection of in-house resources, and maintain mode switches to select the source of maintenance for the project.

Each project should be capable of being installed, configured and operated independently. The installation steps, dependence, data selection and official orders are provided by the project.

When a common methodology is developed, you can identify the problems, the conditions under which it is established and how the same facts are obtained in different organizational forms. Skills are written in terms of the applicable circumstances, the basis to be checked, the method of judgement and the conditions for its completion. A unique catalogue of the project, the order and the agreement are kept in the description of the corresponding project.

### Project resources

Use the project’s bound Python interpreter and documented dependency setup. Keep raw data in the workspace’s shared `data/` area and follow the dataset skill for preprocessing and reusable caches.

## 1. Main Directory of ResearchHarness

- `.agents/skills/` Preservation of skills for any scientific project.
- `src/harness/` provides access to shared skills, tied in-house resources, review of structural results and independent tools.
- `src/project/maintained/` Saves the central identity by project, shares the set-up, works experience, binds the in-house resources and structural results.
- `.workspace/` Keeps central project registration, operational status and development products.
- `pyproject.toml` Configure packages and development tools.

## 2. When can we modify ResearchHarness?

The general scientific mission is carried out within the corresponding project.

**It is currently in the development phase. ResearchHarness Users must clearly approve the scope of the change before the source, configuration, specifications or directory structure is available.** Central Harness Reconstruct the implementation to the extent explicitly approved by the user.

The scientific project code reviews, plans and collaborates with the project’s GitHub process. ResearchHarness uses current user-authorized and operational identities for its own operation.

When the user requests the addition of a Harness feature, the user is asked to specify the following: the gap between current capabilities and needs, how the new functionality will be used in the operation, and which documents are expected to be added or modified; and if the functional meaning or effect needs to be clarified, the user is asked to specify the objectives.

When the user requests that Harness be scaled down, the context of the use of the document or mechanism to be deleted, the actual caller and the removal effect are identified, and the specific option to be reserved, merged or deleted is given to the user. The reservation and consolidation should be based on the actual use, and the deletion is aimed at removing the approved mechanism directly.

### It is forbidden for an assistant to change the layout of the project

**The assistant is forbidden to change the project layout and layout-related parameters.** This article applies to ResearchHarness The assistant must follow the current layout and work in a given location..

When there is a need for change, the assistant must send the request through the current dialogue or human-designated channels, which will be determined and processed by humans. The request must state the rules in force, the catalogue or parameters to be changed, the reasons why the existing zoning cannot be taken over, and the effect of the change on long-term maintenance.

Each request must be accompanied by the following original text.

> Now the agent in charge of harness maintenance has made a request to design a modified project playout. Most of the time, this request is wrong. Playout should not be changed at will. It is suggested that you understand the need to remove it from the playout. For example, why one of the new folders should be included in a level 1 directory rather than in other divisions. AI may judge on a specific issue, but the purpose of playout is to maintain the long-term operation of the project. If the playout can be changed at will, it will be difficult for the code to be organize.

### Research Harness, daily maintenance of your own.

#### Identification of changes from the user portal

1. Finds the user, the existing command or skill, the input, and the actual result. Follow the project source code, the data path, the selected Python, the structure page or the tool to confirm where it will continue to be used.
2. Central access is responsible for the sharing of skills and the binding of the machine. The project’s own operational portal is responsible for scientific calculations, precheck, recording and results. ExtractStructure generates and displays structural explanations. Central structure registers link credible export and review decisions to reviewable versions. The project collaboratively reviews the GitHub process.
3. Modifys the responsible module and direct caller within the user's authorization. Synchronizes the instructions, sample and check the actual use.

#### Maintenance of shared skills and regression tests

When new or updated skills are created, the triggers, the facts to be investigated, the basis for the decision and the conditions for their completion are extracted from the true example of the known project. The generic skills are directed to a strange scientific project, and the entry and evidence specific to the project are placed in the description of the project.

The regression test of the central program is next to the module that is being maintained. `src/harness/core/` Maintenance. Project access, resource selection and review of structural results tested `src/harness/projects/`,Test of an independent tool `src/harness/utils/` the corresponding module. The warehouse root `pyproject.toml` Declare the scope of the collection of the central test. The reference template and the scientific projects maintain the test on their own..

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

Validation operations are carried out under human authorization. Access projects can be validated with one-time enabling changes to the project `rh projects apply <project-id> --lightweight-checks on`. This option covers the central read-only inspection and the use of existing project validation portals that already have in-house resources. Unenabled projects and ResearchHarness's own validations are performed under this explicit mandate.

### 6. Streamlining principles

Functional and binding reservations are based on a clear and effective practical role.

### 7. Principles of writing, interpretation and dialogue

This principle applies to writing documents, explaining problems to and communicating with humanity, with a view to ensuring that human beings can understand what is written and said.

1. **Use a name to describe actual meaning.** When writing titles, naming or quoting chapters, functions, rules, schemes and other objects, use a name that explains the object or purpose, and lets the reader see the name to know what it means. It is prohibited to refer to anything with a numbered letter or number, and to package with a technical term that can be described directly. Such numbers and words do not themselves convey meaning, and the reader needs to find a different description to understand them. When using a common professional term, for the first time, it is used to indicate what it means in the current context, as required. When a proper reference is made to an official name, file path or machine interface, the original name is used..
2. ** Use the full natural language. ** Consistency of abbreviations and code expression is replaced by a full description that humans can understand directly.
3. ** describes the concept and connection in a positive sentence. ** describes directly the meaning, role, interrelationship and application of each concept, with the concept distinction and boundary statement in a positive sentence.
4. ** Provides details on the basis of human needs. ** Daily writing and communication is based on understanding of practical problems, uses and results; technical details and implementation boundaries are then developed when humans clearly request them.

#### Options for sharing information

Within the current mandate, the assistant is responsible for obtaining the facts, completing the engineering judgement and continuing the task, and humans provide, inter alia, the purpose, actual use of feedback and input preferences. When a choice requires humans to provide new intent or a trade-off judgement, the assistant describes the circumstances, viable options, practical implications and recommendations; and technical issues with significant implications explain the conditions and consequences of the occurrence.

**Select the content to communicate around the results of the mission.** The dialogue helps humans to understand actual changes, deal with problems and make decisions. Normal implementation, necessary checks and routine tailings are part of the process of completing the task, with a direct indication of the results obtained and their actual use. In case of problems that affect the completion of the task, the location and resolution of the problem are continuous; where human involvement is required, the circumstances, actual impact, identified reasons and viable options are stated. The examination process and its evidence are kept in the corresponding working information; human inquiries, or the results of the examination affect the current conclusion, what is observed and their impact by functional description. Progress indicates that new discoveries, important decisions and practical obstacles are built around new findings..

**Report completion and remaining gaps without waiting for follow-up questions.** Pursue the user's intended outcome as far as the current authorization and available means allow. State what was achieved and verified. For each incomplete, partially completed, or unverified requirement, explain:

- **Remaining gap and core cause.** State what the user still cannot do or verify, and name the condition that blocks or limits it.
- **Attempts and evidence.** Describe the actions already tried and what happened. State when a step has yet to be attempted.
- **Next action and exact obstacle.** Explain what would close the gap and why that step has yet to happen. Distinguish an unresolved choice by the assistant, unfinished work, a required user decision or authorization, and an external technical or environmental limitation. Name the missing decision, permission, resource, or observable failure where applicable.

Explain the cause and its consequence in plain language so a reader unfamiliar with the implementation can follow why the next action matters. Continue with available in-scope work before reporting completion. When the user requests only an explanation or status, report the available evidence and the remaining steps.

**Direct delivery of documents for download and external review.** Humans need to download documents and provide directly the results that can be downloaded during external review or analysis, by default containing the main information and necessary instructions to complete the use. Individual documents can be delivered directly and multiple documents that need to be handed over together can be compressed packages; humans will be required to deliver in their specified format or content range..

## 4. Opening statements for all Harness documents

Each activity maintained by ResearchHarness Markdown, Python, configuration or other document should begin with a statement that:

- ** Purpose and main function **: Why the document exists, what specific functions it provides, or what data it keeps.
- **Scope of application **: which tasks, modules or operations will read or modify it, as well as the subject subject, trigger conditions and operational boundary.

Markdown documents used to bind Harness have a uniform positive sentence and, in particular, in the section “Purpose and main function” and “Scope of application”, should be precise in describing roles, functions, conditions of application and factual circumstances.

Markdown uses these two same-name subsections; Python can use the top-module document string; the format supporting the note can use the file header annotated. Machine files such as JSON maintain a legitimate syntax with the current data format, describe a programme that is readable in a compatible manner and allow the user to decide on the specific form.

When a restricted Markdown uses the Markdown link to quote another Harness binding document, the reference should be accompanied by a statement of the " Purpose and main function " of the referenced document and the " Scope of application " , consistent with the statement at the beginning of the target document. Each link should serve the actual reading needs of the current task.

Read and maintain a description of the current mandate. This relates to the description of the current mandate document, which is amended in conjunction with the corresponding maintenance; questions affecting the understanding, execution or mandate decision are presented in the context of the specific impact.

## 5. Select the special document according to the current task

- [Access and maintenance of scientific projects](src/harness/projects/README.md)Summarize project access, cataloguing, operating acceptance and inspection and project documentation specifications for access, collation and maintenance of scientific projects.
- [Central work area, in-house resources and project inspection](src/harness/core/README.md)Description of the routing, resource binding, atomic preservation and inspection report, applicable to the organization of the work area, selection of the machine ' s resources and maintenance of the central realization.
- [Transfer & Relief](src/harness/utils/transfer/README.md)Description of the parameters and results for downloading, uploading, checking and selective decompression, applicable to tasks that clearly require the processing of documents or maintenance tools.

## 6. Work boundary at the current stage of development

The actual function is based on a specific program and project portal. Validation follows the light validation option that this authorization or project has already started. Installs a dependent, downloaded data or model, official scientific operation and real data transfer. The project's source code, default scientific configuration, precheck, running records and experimental product return to the project. Centrally binds the saver resource selection, and the structural results reviewer's decision on the specific ExtractScructure version of the page.

The documentation path, cataloguing, naming and experimental product path rules for scientific research projects are governed by the central inspection of ResearchHarness. The overall acceptance is checked `rh projects project check` through `base/`, `datasets/`, `models/`, `tasks/`, `conf/`, physical components and tree-wide paths, and the main function is validated by the public entry point. The assistant performing the specific scientific project task visits ResearchHarness in a read-only manner, using a central read-only inspection, to repair the target project within the mandate.

## 7. Workspace of the machine and attribution of the product

`.workspace/` is located in the ResearchHarness warehouse, which is used to preserve the configuration, operation and development of the machine.

The modular product attribution in this section applies to the operation and development products generated by the central management program `.workspace/`. The resource binding and structural results of a single project are kept at `src/project/maintained/<project>/resources.json` and `src/project/maintained/<project>/structure/`. The experimental operating products of a scientific project (including reference templates) are integrated into the respective project contents `experiment/`. Project skills companion files and local products are stored in their respective skill directories under section 8.

Contents Press `src/` Three main subjects `agent/`,`harness/`,`project/` Organisation, mirroring the actual Level 2 directory. The product enters the corresponding Level 3 directory; the Level 3 directory uses the source file name (deleted) `.py`)or a more deep source code directory name.:

```text
src/harness/utils/probe.py         → .workspace/harness/utils/probe/
```

The project path of `central.py` is `.workspace/harness/core/central/`. The installation-dependent process file is `.workspace/harness/projects/install/`, which is recovered when the installation is withdrawn. `cli.py` Distribution commands are distributed and the product is placed in the actual execution module.

Use the name of each separate file or complete package `<Content or use>_<Project, time or other identifier>`,For example: `project_roots.json`,`environment_saebase-20261103T075412Z.json`,`site_saebase/`.The product is centrally stored in the three-tier catalogue of the attribution module. The complete web page, virtual environment, historical snapshots, etc., is a famous product package; the original file name and content are maintained in the package. The compound package is the module of the organization's package, and the internal call source is described in the log according to the actual sources known to you..

Each of the three-tier directories in use has a short `log_updates.jsonl`. Each new, received or updated product, additional time (time-bound zone), relative path, brief content and source code source; the program is recorded by the appropriate entry and the smart assistant is recorded by the smart assistant manually. The complex package can be recorded once by the member; the log entry object is limited to the product file and package. The source is filled in on a physical basis and the source is written “unknown”.

The old information belonging to the confirmation is placed at `.workspace/tmp/<purpose>_<identifier>/`, where the same log and the original path description is kept. The migration retains the content, permissions and historical identity of the original document; the old path in the original record is kept as a historical fact. The structure results are kept on a specific page, source version, analytical scope and review decision.

## 8. Independence and products of project skills

When adding or modifying project skills in `.agents/skills/<skill-name>/`, use the folder as the complete delivery unit:

- The ** companion file is kept in the skills. ** Use instructions, scripts, references, templates, styles and other running resources are kept in this skills directory; internal references are used in relative locations that can be moved with the entire folder.
- **Specialization of skills required for operation to be kept within skills.** Skills-specific workflow descriptions, process realization, templates and mapping resources are derived from documents in this skills directory. ResearchHarness The public inspection is on duty. `src/harness/core/` Centralize maintenance. Skills can be used to call their public read-only commands..
- ** Operators and operating conditions are clear. ** Skills include user-specified input, operator, target service and necessary running environment tools in their own statements. Read target items, standard tools such as calling Git, or access to target services such as GitHub, which are handled according to specific mandate; these operations are described separately from skills outside the citation directory or customize achievement.
- ** Local products remain in the interior. ** Implementation results, release preparation copies, interim documents, caches, and logs are stored in a generic subdirectories in this skill directory.
- The ** release is aimed at internal copies. ** distribution skills actually copy a user-selected directory or file into their own directory and then prepare the copy for submission, version package and upload. The original release object is read-only, and the document content remains the same as the file collection; Git initialization, construction, packing and writing of the required supporting documents are done within the skills. The release copy is saved by a separate file, the catalogue of work and the writing of the command points to the skills; the initial content of the copy is consistent with the user-selected range, and the adjustments to the release content are processed with the user ' s express authorization.
- **You can continue after moving the whole thing..** The program locates the matching file and product according to the skill ' s own location, and the project path and release target is clearly assigned to the task..


## Public access and support functions

| File or directory | Current responsibilities |
| --- | --- |
| `src/harness/cli.py` | Distribution of project and stand-alone tool orders. |
| `src/harness/central.py`、`src/harness/core/workspace.py` | Positioning the machine project, atoms are recorded in the central record and the product is registered. |
| `src/harness/projects/` | Connect to central maintenance to manage in-house data, Python and structural results. |
| `src/harness/utils/` | Process transfer, depression, process environment observation and snapshot comparison. |
| `src/harness/core/` | (b) Maintain central checks of the use of shared skills and their regression tests. |
