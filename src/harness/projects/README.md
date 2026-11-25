# Access and maintenance of scientific projects

## Purpose

Provides an operational portal for project access and sharing of skills, along with documentation, operational acceptance and documentation standards for scientific projects.

## Scope

The project operates independently on its own dependencies, configurations, and commands. The routing and central inspection report can be found in [Central Work Zone, in-house resources and project inspection](../core/README.md) for location registration, resource and verification.

- [Access and Usage](#project-setup)Helping to register projects, synchronize skills, bind resources, initiate orders and manage structural results.
- [Catalogues and documents attributed](#project-layout)For checking paths, layouts and naming.
- [Run and accept](#project-execution)Description of precheck, experimental records and researcher review.
- [Item documents](#project-documentation)Show me what you're supposed to write on the pages..
- [CUB-200 Items for information](templates/cub/README.md)Show configuration, components, pre-check and results with a runable example of classification.
- [Catalogue of scientific project templates](templates/README.md)Provide replicable project source code, configuration and operational access, applicable to mission-specific access items. CUB Default Reference.

<a id="project-setup"></a>

## Access and Usage

### Overall and dedicated maintenance of the project

The **[`maintain-project`](../../../.agents/skills/maintain-project/SKILL.md) is the main entry point for the overall maintenance of the scientific project. ** applies to access to strange projects, to combo catalogues, to check the existing project as a whole and to process cross-component changes.

The following specific skills are used directly when handling a single job. `maintain-project` Coordination, tailored to actual gaps and affected behaviour.

| Skills | Application of work and duties |
| --- | --- |
| [`maintain-base`](../../../.agents/skills/maintain-base/SKILL.md) | Connect commands, configurations, data, models and missions, maintain distribution, share operational resources and read and write results. |
| [`maintain-dataset`](../../../.agents/skills/maintain-dataset/SKILL.md) | Add and remove data sets and presets, and maintain sample preparation, division, registration and task reading. |
| [`maintain-model`](../../../.agents/skills/maintain-model/SKILL.md) | Adds or removes models or variants to maintain their construction, weight loads and mission compatibility. |
| [`maintain-task`](../../../.agents/skills/maintain-task/SKILL.md) | Adding or removing scientific missions, models or results interfaces, and maintaining the interface of calculations, indicators and results. |
| [`maintain-conf`](../../../.agents/skills/maintain-conf/SKILL.md) | Add, remove or modify public parameters to check meanings, default values, coverage and historical compatibility with actual consumers. |
| [`maintain-experiment`](../../../.agents/skills/maintain-experiment/SKILL.md) | The report is maintained using the experimental formulation and the single parameter to perform, track, restore, read or screen experiments. |
| [`maintain-optional`](../../../.agents/skills/maintain-optional/SKILL.md) | Maintenance of independent scripts, tests, component documents and external documents kept with the project. |
| [`maintain-tmp`](../../../.agents/skills/maintain-tmp/SKILL.md) | The catalogue, use and closure of the one-time project work is managed and applies to short-term scripts and documents that cannot be carried out at the existing entrance or official location. |
| [`maintain-code`](../../../.agents/skills/maintain-code/SKILL.md) | Review and maintenance of designated codes and their upstream and downstreams, and cleaning of temporary documents once the core results are reproduced through the public entry point. |
| [`maintain-skill`](../../../.agents/skills/maintain-skill/SKILL.md) | The specified skills are assessed in real-use scenarios, the results of which are biased and are repaired and repeated. |
| [`maintain-knowledge`](../../../.agents/skills/maintain-knowledge/SKILL.md) | The organization and preservation of knowledge worthy of long-term use applies to the recording of ideas, reading of existing knowledge and additional comments. |

### Connect a project

Use the project's README to install dependencies, configure data and the environment, and run its normal commands. The optional ResearchHarness connection gives the project access to shared skills, local resource bindings, and structure reviews. See the [workspace and resource guide](../core/README.md) for path resolution and workspace setup.

For a project in `example/`, run these commands from the shared workspace:

```bash
rh projects --harness-root ./ResearchHarness register example --path ./example
rh projects --harness-root ./ResearchHarness setup-maintenance ./example --online
rh projects --harness-root ./ResearchHarness status example
```

### Online and offline maintenance

`rh projects setup-maintenance <project-root>` installs a mode setting, a status and check command, and an offline guide. It also updates the managed section of the project's `AGENTS.md` and clears known legacy ResearchHarness links and generated guides. Project-owned skills stay in the project. A standalone project starts in offline mode. An existing project uses its current mode file or last applicable connection setting. To set up a new online connection, register the project first and then use `--online`.

The `enabled` value in `.researchharness/mode.toml` selects the maintenance source:

- With `enabled = true`, run `python -IS .researchharness/maintain.py status` to locate the online guide in the ResearchHarness workspace. It links to the central operations guide and original shared skills. The project's `.researchharness/online/` holds local connection records. Use `rh projects apply <project-id>` to refresh the guide after configuring or restoring a connection. An unavailable online connection returns an error so the user can restore it or choose to work offline.
- With `enabled = false`, the maintenance launcher uses the project's offline guide and local checker.

A project without a mode file can continue using `rh projects set <project-id> --skills on/off`. With skills enabled, the managed section in `AGENTS.md` links to the central originals. With skills disabled, it points to the project's own maintenance instructions. The project uses `.agents/skills/` for its own skills.

Setup and synchronization refresh the same search guidance in the project's `AGENTS.md` in either mode. The [CUB maintenance instructions](templates/cub/AGENTS.md) show how to choose the mode and run the status and check commands. The mode file, launcher, and offline materials travel with each project. Installation and research dependencies are described in the project's own documentation.

<a id="project-publishing"></a>

### Publish a project

Projects with offline maintenance or no ResearchHarness connection choose their own publishing process. Put their GitHub release configuration under the project root's `.github/`.

For projects using online maintenance, `maintain-github` handles release preparation, comparison, and delivery. Its internal copies hold release, upload, and deployment scripts and configurations. The skill prepares the diff and any build or package, then pushes or creates a release within the approved scope. Project installation, build, run, and test commands remain available in both modes. The project's `.github/` can also handle continuous integration, code review, and issue collaboration. Apply the relevant workflow when changing modes and migrate only the approved files.

### Daily maintenance and light authentication

Once the same item has been maintained several times, it will be available once the central index has been approved `rh projects maintenance <project root directory>` View the change and last check conclusion. Commands to keep the file ' s state, reusable structural judgement and existing maintenance records in the centre. `.workspace/harness/projects/maintenance/`.It judges changes by the file system properties, reading the source code or configuration body on demand. The whole structure report is used when neither the project nor the inspection rules change. `reused` and original check time,`--fresh` Force re-acquires. A directory link may point to content outside the index range and re-examining the structure check when such a link exists.

Use it. `--record <JSON File>` Writing maintenance records. JSON Organisation `entrypoints`,`issues` and `evidence` list, replace the previous record as a whole when saving. `--limit` Displays and attaches the total number. The running evidence is kept as a historical record and checked by command, valid configuration, data, weights and operating environment before reuse. `project check` Still available for independent read-only acceptance and inspection.

`apply` Writes in a central online note a link to the operating classification, fixed drop-points and applicable specific skills. Old access items follow the managed paragraphs of the item `AGENTS.md`. The list goes directly to [maintenance item](operations.md), which describes how each type of request will be judged, how it will be done, how it will be chosen in different circumstances, and how it will be validated and completed. Each day-to-day operation will be carried out according to the corresponding chapter. Ordinary tasks will follow the existing level-I catalogue, which will allow for the first use of a standard catalogue and level-I directory to adjust the use of clearly approved project access or structural maintenance.

When you receive the "Access to a function", position the responsible position in the nearest current command from the user's desired entry, input and result. First judge whether the existing parameters will meet the request, then decide whether to expand the existing component or add a new independent component. You move on to the task, then connect to the registration, configuration and result of the actual change. Finally, check the target's behaviour and writing position from the same entry. The template below gives examples of actual files and complete operations.

The user wishes to operate once from the parent's work area when the light-weight check is included in the daily maintenance:

```bash
rh projects --harness-root ./ResearchHarness apply example --lightweight-checks on
```

Select to save at the project 's home `project.yaml` , Available `status` View. Again. `apply` Follow saved settings, use `--lightweight-checks off` Closes. The old project defaults on a sequential authorization. The project guide is suspended when the shared skills are closed, and the saved option is restored when the skills are re-enabled. The command is synchronized, and the light check is performed by the assistant on a specific skill basis after the subsequent changes have been completed..

Use `rh projects layout check` for local structural or name changes. The result is repeated in the same tree state using `rh projects project check`, which already contains layout rules. Experiments and pre-test reviews are subject to the corresponding central read-only command. Behavior changes give priority to obtaining evidence from existing tests, configuration previews or pre-screens of the project.

### Inner data, Python and structural results

`rh projects bind`, `resources` and `run` manage their own path and use the selected Python to call the original entry to the project. Use `{data:name}` to send the registered data directory to the project's parameter or environmental variable. `rh projects install` Use the same Python installation statement to rely on.

The binding record is kept at `src/project/maintained/<project>/resources.json` for ResearchHarness. Structure results and review records are kept at `structure/` under the same item directory.

`rh projects structure add` Receives a credible independent HTML exported by ExtractStructure, as well as source versions and analytical ranges. Use `list` or `show` to find a page and use `review` to record the decision on that version. View the page directly to open the path to the machine to which the command returns.

[Use Example](../../../README.md)Description of the specific calls for installation and commands, applicable to new project access and to the home-based operation of existing projects.

<a id="project-layout"></a>

## Catalogues and documents attributed

### Overall layout and necessity

When accessing a strange project, a whole combo catalogue or reconnecting multiple components, use [maintain-project](../../../.agents/skills/maintain-project/SKILL.md) to identify responsibilities from the real entrance, organize specialized maintenance and check changed use links.

The following table shows the functions of the root list of the project. Each scientific project has an entity-level catalogue `base/`, `datasets/`, `models/`, `tasks/`, `conf/`. The total acceptance is `rh projects project check <project-root>`, which contains a detailed tree-wide path check. `rh projects layout check <project-root>` is referred back to the physical tree and reports the path and non-compliance terms. The whole project acceptance is based on the withdrawal status `0`. The specific path and documentation rules are implemented by `src/harness/core/layout.py`.

| Location | Required level of preparedness | For what? |
| --- | --- | --- |
| root directory `README.md`, `AGENTS.md` | Required | The former describes the purpose of the project, the entry point for normal operations and the location of the results, while the latter describes the maintenance of the rules within the project and locates the common agreement. |
| `conf/` | Required | Provides `conf/config.<format>` for official access and effective formulations. |
| `datasets/` | Required | At least one actual data set and its reading, preparation or disaggregation is achieved. |
| `models/` | Required | At least one actual model and its construction, loading or call realization. |
| `tasks/` | Required | There is at least one actual scientific mission, with an additional `precheck/` to provide an automatic precheck for a formal mission. |
| Workspace Data Roots | Use when entering accordingly | Original scientific data sets, source-distributed labels and directly accompanying data files are placed in the working area at `data/` on the project level. The first-level list of directories of the project root excludes `data/`. |
| `experiment/` | When there's a scientific operation. | A fixed list of experimental products under the root directory. The running entrance is located from the root of the project and automatically created when you write it first. |
| `base/` | Required | Saves real open access, configuration synthesis, component selection, task distribution and common running support. |
| `doc/` | Required | From README navigation to document index, provide a description of the actual level I directories and connect components, parameters, experiments, knowledge, implementation environment and source structure. |
| `tests/`、`scripts/`、`third_party/` | Optional | Automatic regression, manual running tools and third-party source code are established on a practical basis. |
| `assets/` | When resources are retained for a long period | Fixed presentations, stand-alone re-uses and other long-term resources maintained with the project are grouped by type and use, together with source descriptions and dedicated scripts. |
| `tmp/` | When there's a one-time project | A list of names is used for each job and ends as intended. |
| `.researchharness/`、`.agents/skills/` | Created when connected or self-skilled | The former preserves project statements, while the latter are used for project-owned skill discovery. |

The root directory is used primarily for navigation, installation and access; the component logic, configuration, documentation and running files are each assigned to them. The secondary directory is created only when the corresponding duties actually appear. A small number of files can be flat, the duties specified and then decoded into a generic directory. The project structure describes the actual command, the catalogue map and the open path available to help the assistant to take over by pressing the existing entrance.

The project root name uses two or three words, PascalCase, such as `ContextMemory`, which contains at least one full English word. The self-defined directory and file name contains at least one full English word, giving preference to a word named sub-task, with multiple words separated by underlined. Real models, data sets and their versions can be distinguished by numbers. The directory of these components in the configuration mirrors follows the same place. The file, the external resource content and the executing identity in the running records specified in the framework follow the same format. The tree-wide examination reports on the project root name, numbers and vocabulary problems.

The code checks to overwrite the visible project content. The hidden path and Python byte-code caches are left to their respective tools. The checker reads the experimental identity from the actual project component directory and the component directory map of the main configuration `conf/config.<format>` and checks the configuration from the actual source directory. The function is whether the project is actually enabled, the path corresponding code is actually called, and whether the same functionality can be combined and validated along the normal entry.

### Base level and scientific components

Command access, open interface, movement control, and general operating codes to enter `base/`, sample and classification to enter `datasets/`, model structure and reasoning to enter `models/`, and training, assessment, laboratory computing, and mission-specific indicators to enter `tasks/`. The installation name can still be maintained through a packaged map or thin entrance, and the original open import can point to the end of the split.

The central inspection requires five entity directories, `base/` portals or operational realizations, `conf/` configuration portals, and real source codes for data sets, models, official missions. Empty directories, placeholder realizations, registrations and precheck alone cannot serve as components. Check `base/` embedded component source trees, and limit direct documentation to 15 per layer at `base/`, `tasks/`, `scripts/`, `tests/` and recognizable old source roots. `datasets/` and `models/` subtrees exemption numbers are still subject to acceptance.

When there are more than 15 direct subdirectories, `project check` reports the path, number of files and number of subdirectories by `directory_reviews` for functional inspection and repair. The independent functions in the existing directory are based on actual calls. The number of documents remains at the mandatory limit of 15.

The central structure checks the disk and the actual call evidence that the components have been correctly connected.

| Level 2 directories or files | Enable Conditions | Documentation duties and access rules |
| --- | --- | --- |
| `commands.py`, `__main__.py` or equivalent entry in `base/` | When ordered | Parsing parameters, selecting actions, showing results or malfunctions. Command lines and other callers revert to the responsible module. |
| `base/` Medium `runtime/` | When supported by project-level running | Runrs call for data, models and tasks. Path resolution, configuration synthesis, operating environment and records are organized according to their actual duties. `paths.py`, `config.py`, `runtime.py` and `records.py` are the filenames that can be used to assume the corresponding responsibilities. The CUB template is `base/cub_template/runtime/`. |
| `base/` Medium `interfaces/` | When there's a steady external call | The entry indicates input, return value, failure condition and compatibility range. |
| `plugins.py` and `registry.py` for the base level under each component directory | When multiple components need to be individually configured | The various components catalogues maintain a login to the entry point. |

#### Standard catalogue for three types of components

```text
datasets/
├── plugins.py
└── <dataset-or-family>/
    ├── __init__.py              Open access and supported tasks
    ├── dataset.py               Create when there is an independent official reading
    ├── prepare.py               Create when independent data preparation steps are available
    ├── transforms.py            Create when independent data is changed
    └── <member>/                Same-source queue or data subset is created when a separate file is required
models/
├── plugins.py
├── build.py                     Model shared build-and-declaration interface
└── <family>/
    └── <series>/
        ├── specs.py             An optional variable and resource statement in a series
        └── model.py             Created when the series is dedicated
tasks/
├── plugins.py
├── <task>/
│   ├── task.py                   Task interface and validation
│   ├── operation.py              Job Count
│   └── evaluation.py             Established when steps for independent evaluation are in place
└── precheck/
    ├── task.py                   Independent precheck mission
    ├── gate.py                   Pre-check call for a formal task
    ├── timing.py                 Time-consuming phase of measurements
    └── performance.py            Bottleneck analysis, comparison of candidates and decisions
```

The official data set has a stable catalogue. Accomplishments for the simulation of samples, labels or classifications for a given data set are placed in the DDS. Multigroups call for actual common realizations to be placed on the public level. Model series statements can contain multiple public identifiers, which follow the built-and-loaded path of the new series of variants. Only when new families or series are added. Configure presets, open identification and location are maintained by registration, and a callable entry is in place. The common logic across multiple components is maintained in terms of actual reuse.

The data family shares the source and prepares or reads the contract, the model family shares the structure and weights agreed, and the task family shares the purpose of the study and the output. The independent queue, model variants and sub-tasks still have optional identifications. The father's directory saves only the common code, rules or entry that its members actually use.

Subtasks determine boundaries by means of self-described research steps and their inputs and products. The name module of the mission for which the calculation or evaluation of the subtask shared by the same task is assigned, cross-task data reading, model behaviour, training status and document reading and writing is provided by the data, models or operating layers for which the actual responsibility exists.

| Component | Input and Delivery | Rule |
| --- | --- | --- |
| Data Set | Receive data configuration and actual path or source, deliver samples, divide and enter identity | The classification and labeling meanings are defined by the data set. The official input and the synthetic input are identified. The data are prepared as identifiable operations, and the data files are in the data. |
| Model | Receive model configuration and required weights, deliver callable model and clear input output | Training objectives and evaluation indicators are defined by the mandate in which they are used. |
| Tasks | Receive configuration and selected components, complete training, assess or analyse and deliver indicators and results | The pre-check uses the same component and mission step, and the public operating module records configuration, environment, state and product location. |

Configures the selected components by using the only entry for the project. The existing items can be used for registration or selection. When separate components are added, the component realization, registration and formulation are added, and the general command, precheck and running records continue to be used along the existing interfaces. Available options are given when searching for the unknown identifier, and the original identification and formulation are made publicly available.

The components examine the parameters they have, the tasks check whether the selected data and models can be implemented together, and the public operating modules call for them before actually loading the resources. Task-specific indicators, measurements and report syntax are maintained. A mission can be trained, analysed or evaluated under the same objective of the sub-mission. Sub-mission declarations are entered, exported and called, and the public inspection and results are coordinated by the task to which they belong. The common operation of the individual and long-term caller is placed in a position of actual responsibility and is called by multiple tasks.

Template `cub200` and `synthetic` Intersection using the same disaggregated data,`resnet18_mlp` and `small_cnn` It's all possible. `classification` Select. The master configuration uses Hydra Configure Group Independent Selection Component. `tasks/precheck/` The time, baseline bottlenecks, and candidates are compared. `tasks/precheck/`,The operational module provides the public equipment to synchronize and save access to the fixed sample view..

### Configure & Relative Path

When a layering is used, the parameter prefix represents the actual owner. Each subtape under the task has its own prefix, and the shared setting is maintained by the task or cross-tape in a uniform operating layer. Output values, such as output identity and path, are generated from the operating layer and the specific study combination is saved by the experimental formulation.

`conf/` organises a default set of project configurations. The reference template is used `conf/config.yaml` in a single format, and the default parameters and optional component definitions are concentrated in this file. The configuration of the specific experiment is kept as it runs at `experiment/`, README gives the official access and coverage.

| Configure Paths | When will it be used? | Save Contents |
| --- | --- | --- |
| `conf/config.yaml` | When the project adopts the unified configuration portal | Default component combinations and shared defaults, loaded by the normal entry. |
| `conf/<relative-source-directory>/` | When data, models, tasks or running components are actually readable configurations | The relative directory where the responsible source code is located is taken from the root of the item and the two-stage path is maintained under `conf/`. For example `tasks/capture/` corresponds to `conf/tasks/capture/`. |
| Responsible for running the configuration directories of the modules | When the environment, device or path needs to be configured independently | The interpreter, device or the configuration of the input path is placed in the directory that actually loads and validates their operating module. |

Up to two-tier directories under `conf/`. Each configuration branch has one file. Deeper duties are combined into a named section of the corresponding file. For example, `conf/tasks/capture/task.yaml` also saves default values, batches and filters for capture tasks, with each entry reading the respective section.

The configuration of new, modified, moved, removed and deployed must check the source code and configuration path and verify that it is loaded. Check the submission, continuous integration and release of access items. The configuration changes are automatically synchronized to `doc/conf.md`, indicating that the semantics in the description are maintained by code.

When adding, removing or modifying the open parameters, cross-checking the configuration file attribution and document synchronization with [maintain-conf](../../../.agents/skills/maintain-conf/SKILL.md) for actual consumer processing parameters syntax, default values, overlaying and compatibility.

The project entrance determines the root of the project, and the base level resolves the default configuration and the default configuration at the agreed starting point `experiment/`,The data is obtained from the working-area data root. Components receive the actual path. The path within the new formulation defaults against the project root. A formulation already exists that follows a clear set of relative rules, such as: CUB Data path relative to the formula directory. README Defines where the command line path starts and the formula path starts, respectively. Actual data, external weights and the machine Python Give it to the project by means of a named binding, parameter or environment variable..


### Testing, description, manual tools and third-party information

The source station that needs to be built by the document tool is located `doc/code/<Name Document Station>/`.Site directory to save build entrances Makefile,make.bat and requirements.txt,Build input in `source/`,Keeps the internal file name, cross-reference and static resource address used in the document tool. Syncs the open build or deployment portal. Generates pages to save for their delivery or cache uses.


| Level 2 directories or files | When will it be used? | Save content and boundary |
| --- | --- | --- |
| `tests/test_<behavior>.py`、`tests/product/` | When functional behaviour requires continuous review | A small number returns to the root layer, forming a group of continuously maintained products and then returning. `product/`.Filename locates actual behaviour or entry. |
| `tests/integration/` | When there is an independent cross-component, real service or environmental link check | (b) Maintain chain testing, with an indication of operating conditions, actual resources and coverage. |
| `tests/fixtures/` | When multiple groups test the same small sample | Keep a description of the small fixed input, the expected results and the source of the need. |
| `doc/code/` | Project document portal | Navigate to `extract-structure`, the project structure results and their source version. Examples of architecture, interfaces, transfer of components and projects are here. |
| `doc/knowledge/` | Project document portal | (d) Preservation of scientific concepts, terminology, interpretation, basis of agreement with the project, citing actual sources. |
| `doc/environment/README.md` | Required by `doc/README.md` link | Saves relying, interpreter, equipment requirements, operational readiness and light authentication methods. The physical environment is read from the corresponding run records. |
| `scripts/examples/` | When there is a stand-alone demonstration | Saves the presentation portal, and the thin script is officially achieved. |
| `scripts/<purpose>/` | When another group of operations has a clear user | Saves the instructions, access and necessary configurations by use. The calculation has been re-used for the official task and is moved to the responsible module. |
| `assets/<resource-type>/<resource-name>/` | When resources are retained for a long period | Recording uses, sources and updates with `README.md`, preserving resources with `files/`, and preserving resources with `scripts/`. |
| `third_party/<upstream-name>/` | When a third party source is actually retained | The location of the upstream project management package, where the upstream physical path and file name are maintained. |

`tests/` is optional, and the actual change check is selected by [the maintenance inspection rules of the project agreement](README.md#maintenance-checks). When the project has a specific pre-check, audit or client test, register its real entry and existing grouping.

The script directory is organized according to the user's operating organization. Multiple entry points perform the same job and maintain the same entry when differences can be expressed by name parameters. Project documents describe the official components to be called at each entry, the type of input to be entered and the way to view the results.

### Data, operation and access information

| Location | Enable Conditions | Documentation responsibilities |
| --- | --- | --- |
| Workspace `data/<dataset-name>/<version>/` | When using source data sets | Saves the raw data, the indication provided with the source and the release file or index that directly matches the version. The project configuration points to the actual data root and runs the input identity used for record-keeping. |
| Item `assets/<resource-type>/<resource-name>/files/` | When project independently reuses preparation results or caches | Saves pre-prepared input, fixed set of questions, model answers and annotated cache of items obtained. `README.md` Recording uses, sources and how to update. The locks and temporary storage of data preparation follow the actual writing position, and atoms write in the same file system. |
| Project level `tmp/` | One-time engineering work that cannot be carried out by the existing public entry point or directory | The code, configuration, and document of the other level I directory point to the official document. `maintain-tmp` Review for conversion or clean-up. |
| `experiment/<dataset>/<model>/<task>/<subname>/<optional-run-role>/` | When the result is generated | `subname` Describes the experiment or the object of exploration in one or three lowercase English terms, under a single underlined word. The subtasks or the name of the experiment under the mission are named according to the actual function, the purpose of the exploration or the key parameters that make up the conditions of the study, and can be grouped as required. Each level provides information that has not been expressed by the superior. The executive layer is only enabled when there is an independent use or control role. Serial numbers, dates, seeds and other parameters are written into the configuration or execution record. Repeated execution of the same use and role is distinguished by the list. |
| `experiment/<dataset>/<task>/<experiment-name>/<optional-run-role>/` | When studying the calculation directly to the data | This type of operation saves the model layer. |
| One run `config.yaml` or the configuration format used for the item | Configure successfully after parsing | Saves the configuration with the default, selected components and overwhelms. The running list points to the file. |
| One run `metadata/` | When a run result to be handed over | The `manifest.json` is the default reading portal, which can register the equivalent path. Configure, precheck back, place the environment record here or quote from the list. |
| One run `reports/`, `logs/`, `artifacts/`, `tmp/` | When corresponding output is available | Readable reports, process logs, usable products, and temporary materials are assigned separately. |
| `assets/history_experiment/<result-name>/` | Keep existing experiments or demonstrations | `README.md` Description of uses, sources and modes of reading.`files/` Keeps an internal directory, filename and source-code snapshot of the frozen original. `experiment/` Operation through identity, effective configuration and product inspection. |
| `.researchharness/project.yaml`、`.researchharness/central.json` | When using the respective access function | The project is subject to a central project order. |
| `.agents/skills/<skill-name>/` | When there's a project with skills, | The project maintains its own skills, each of which provides `SKILL.md`. |

Component identification, catalog and Python files are used in lowcase English to describe their use, and multiple words are underlined. Formal interfaces and upstream original names are used in original form. Keep dates, times, hashes, and execution identifiers in the run record. Every experiment directory segment and output filename stem uses at least one complete English word. Optional named execution directories use the descriptive `execution_name` from the manifest. The machine `run_id` may contain a timestamp or UUID as metadata. The new directory indicates the conditions under which they are enabled, the actual caller and the corresponding entry, and is synchronized with the protocol [the example of the layout of the reference item](templates/cub/doc/code/development/layout.md) to compare the changes to the project catalogue and additions.

The project allows a stable match between the public component identifier and the disk spelling. Read the corresponding rules for writing the statement of the oral re-entry project, and run the list to save the actual component identifier. Select the same path from the same component for acceptance.

The data sets and models in the experimental path are functional. When the project has a real family and has multiple independent members, you can express the family and members in two segments at that location, such as `<dataset-family>/<cohort>`. The family name appears once in the patriarchy, and the members ' catalogues write their unique identity. Start, read and document together use the relative path from the public identification.

`experiment/` The results of the joint analysis are assigned to the public entry point of the analysis, the path is determined by the actual master data or registered joint input, and the members and sources are kept on the list. `maintain-experiment`.Source data using a registration number can be identified by Queue Name, the list retains the original number and normally writes the same correspondence to read.

`rh projects experiment check <project-root>` Checks the list, configuration, routing and matching of documents to the list in `artifacts/` and `reports/` for formal experiments. The whole project is maintained simultaneously at `rh projects project check <project-root>`. The results include the number of implementations and specific non-compliance paths. The official reading back of the project continues to verify the actual results.

The project's dependency list is placed in the official position, and the interpreter binds and installs the entrance ResearchHarness.Hugging Face Downloads and General Caches By Local Client or `maintain-huggingface` task directory processing. Data conversion results and reusable caches are attributed to the corresponding data root.

### View the landing directory rules from the template

| Something to judge. | Practical practices in templates |
| --- | --- |
| Where's the configuration changed, where the components were called? | CUB `conf/config.yaml` selects data, models and tasks; `base/cub_template/runtime/runner.py` connects components and pre-checks; model variants follow the corresponding model catalogue. |
| When did the two uses become independent missions? | The SAM2 image partition and video tracking are located at `tasks/image_segmentation/` and `tasks/video_segmentation/`, respectively, and are responsible for their respective input and operation. |
| Where are the tests written? Where are the results read? | The CUB `tests/test_workflow.py` checks existing accesses and results; the `runtime/records.py` registration run report, `inspect` is read from the running directory. The SAM2 image reasoning and video tracking tests are named after each other. |

[CUB Example of Engineering Work](templates/cub/doc/code/development/engineering.md)Use the actual source code for the classification items and the results portal to explain how the functions are classified, accessed and validated, and apply to the performance against the request for the performance or maintenance of the function. [Catalogue of scientific project templates](templates/README.md) Find, the template directory provides a copyable source code, configuration, and running access, which is suitable for selecting a similar reference item.

<a id="project-execution"></a>

## Run and accept

### Synchronize protocols with reference items

This agreement is updated at the same time as the [reference item](templates/cub/README.md)]. The project provides a runable CUB-200 classification and project maintenance sample, which applies to learning layouts, the purpose of the certification agreement and the reference establishment project.

- Syncs the actual directories, entry points, references and layout tables in the templates when the directory or naming rules are updated.
- Synchronizes the examples of the code, configuration or real product that is responsible for in the template when running, checking or updating the rules for data handover.
- The trigger conditions and the corresponding position are indicated by a description of the template in accordance with the user-enabled rule. The template is demonstrated by real realization when applied, and other project-specific configurations or behaviours are exemplified by the project ' s own description.
- When reviewing changes, corresponding documents, orders or instructions from the template can be found for each new or revised rule. There are existing items that validate the rules in their actual maintenance and bring back the protocol and template for improvements that are useful for other items.

### Directory and Naming

Access to ResearchHarness is enabled on an as-needed basis to provide the project’s own resource choice through public orders, parameters or environmental variables.


The physical entry and product are tracked from [maintain-project](../../../.agents/skills/maintain-project/SKILL.md), the specific maintenance of the various components of the organization, and the entire link is checked back at the normal entrance when accessing a strange project, inspecting the entire project or maintaining a cross-component process.

The project description records normal commands, configurations, components, operational results and project-specific paths. The root directory contains three types of scientific components. The SAEBase and CUB templates provide actual references to the layout.

** Component Extensions. ** New components are accessed along the official selected entry, with the component checking its own parameters and the compatibility of the task group. Use the existing entry to check the new formulation and confirm that the old formulation is still functioning as it is. Split the component to keep it open and callers do not rely on their internal files. Sharing is achieved on the basis of the actual caller. When changing the common rules, the template must give examples of the corresponding code, formulation or actual work in the same maintenance.

The project using the SAEBASe module combination selects the data, model and task configuration group through the main configuration. The various components are registered in their own directory and are selected and distributed at the operational level. The public interface of the task is responsible for checking and returning the structured results, which are calculated as the task is accomplished. The pre-check is used as a stand-alone task and the actual check-back is saved at the official running entry.


<a id="maintenance-checks"></a>

### File function and maintenance check

The main module starts with a description of the use and scope of application. Data access, calculation and preservation of the results are the responsibility of the clear module, which is the subject of public access; command scripts are responsible for the parameters and organization of the caller; check the entry, the configuration and description affected, and whether the results can be read at a later stage. Open parameters are tracked through the normal entry to consumers and to visible behaviour.

When reviewing the assigned code or processing duplicated realizations, functional gaps, check the code, up and down, and products from a real-use scene with [maintain-code](../../../.agents/skills/maintain-code/SKILL.md), and repair and repeat them within the authorization. When adding, removing or modifying public parameters, synchronize [maintain-conf](../../../.agents/skills/maintain-conf/SKILL.md) with the actual consumer treatment meaning, default value, overlay, old formulation and configuration document.

| Change Type | Countercheck |
| --- | --- |
| Description or table of contents adjustments | Check the physical entry, citation and file location |
| Corrective procedure behaviour | Prioritization of existing tests for the identification of errors from normal access points and recovery results |
| Change public interface or result format | Checks the current caller, old format for reading and failure information |
| Change Research Calculator Path | Use representative input to indicate synthetic or real data and range of comparisons against actual results |

The inspection is carried out on the basis of actual risk and project authorization. Long-term tests and their catalogues are established or extended only when there is a continuous return value.

### precheck, timing and bottlenecks analysis

The whole project goes through the center. `rh projects project check`.Project root has an entity `base/`,`datasets/`,`models/`,`tasks/`,`conf/`,Use normal commands to review the actual splitting of the main function and to retain the original function and result to read evidence..

The project provides `precheck`, which can be independently called under `tasks/`. Each official scientific mission is automatically called before the calculation is made and is then formally calculated after adoption. Pre-test and the official mission share the current configuration, actual data and model selection and formal execution logic. The dependencies, equipment, input, minimum calculation, result path, format and official reading are quickly validated with a very small number of samples and steps. The official mission saves the pre-check evidence.

When using the performance model, `tasks/precheck/` is responsible for budget, phase time, bottleneck analysis and accelerated candidate comparison. Targeted tasks are actually entered, work unit, measurable steps and results consistency determination. The project is based on the stage involved in the actual call chain to record, read or wait, calculate, transmit, drop a disc. The equipment that requires a different step is synchronized at the time boundary, and the report indicates whether the phase overlaps.

Record the number of preheats and repetitions, sample range, workload, environment, numerical strategy, time-consuming and resource peaks at each stage. The bottleneck conclusion refers to the realistic phase of the baseline and its measurement range. Share preparation, candidates' unique preparation, fine-tuning costs, and measured execution separately. Phase-level performance and official mission-end-to-end performance are shown separately.

### Accelerated candidate and adoption

Precheck compares the current configuration with the candidate under the same input, workload, environment and numerical strategy, and preserves the basis for consistency of results, time and resources. Candidates are recommended for application only if they meet established results criteria, resource budgets and actual benefits. Recommendations for prior or partial operations are only available for the corresponding range, and formal training proceeds are verified with official workload.

The report provides the current configuration, candidate configuration, phase cost, revenue, decision and reason. The reasons for rejecting a candidate that has not been adopted are used for formal implementation. When a recommendation is introduced through a configuration or registered strategy, the running list records the actual use value. Checks the model, tasks, size of input and environmental conditions that affect the return and correctness prior to the reuse result.

The full process is demonstrated by comparing the number of work processes with the reference items. The normal entry is used to pre-screen the performance, report the baseline bottlenecks, and then give a candidate for the formulation. [Example of Engineering Work](templates/cub/doc/code/development/engineering.md),For expansive precheck and review results.

### Environmental information

The project records the environment of the selected environment and the operational process. The operational record locates at least the operational settings of the actual interpreter, key software version, implementation equipment and impact results. The report refers to the current operating record or matching snapshot, and indicates the time and source of collection. The central environment snapshot provides the machine background, and the project operating record describes the actual use.

### Run-out delivery

Start, restore or screen the experiment using existing parameters, and check the configuration, result path and readable product from the public entry point with [maintain-experation](../../../.agents/skills/maintain-experiment/SKILL.md), and update the laboratory report with actual evidence when reading already in operation.

Each project consolidates the experimental product into the first-level directory `experiment/` of the root directory of the project. This directory is used for training, pre-checking, performance comparison and the resulting logs, reports and weights. The program is guided by the root, and the configuration and command line selects only the experimental name, the operational identifier and the level of the directory. The reference template is fixed by the running record module.

The first-level position of the experimental tree is determined by the actual input data. The results of the joint analysis are located at its public entry point by the main data or registered joint input, and the records are kept for the actual members and sources. The results of the batch movement groups are read along their respective public entry points and the movement status is managed by the movement point.

`conf/` Centralizes a set of project default configurations. Specific experiments are in `experiment/` Use and save specific parameters against the position. Each experiment uses `subname` Describes the experiment itself or the object of exploration, using one to three words, separated by lower-case underlined. The operational directory is divided by datasets, models, tasks and the name of the experiment with an independent meaning and the implementing role organization. `capture/non_whiten/answer_stability`.The executive layer name expresses the performance use or control role. Serial number, date, random seed and other operational parameters are written in the configuration or list. Duplicate execution of the same use and role is distinguished from the list.

The list refers to the file. The list of recommendations for a single run is `metadata/`, `reports/`, `logs/` and `artifacts/`, `tmp/`. The long-term results are read through `metadata/manifest.json` or the specified price equivalent entry of the item, and the original results and weights are quoted in the list. The temporary information is in an independent location, which is followed by the project's original identity and restoration conditions.

| Fields required for central summary | A promise. |
| --- | --- |
| `schema_version` | List format version, by project record field or map |
| `project_id`, `run_id`, `task` | Project, execution, and task identifiers stored in the record |
| `execution_name` | Descriptive directory name when the execution has its own directory |
| `status`、`updated_at` | Current status and time-time, commonly running, subcredged, failed, blocked, partial |
| `inputs`、`configuration`、`source` | Data, models or other input identities, actual configuration and source version |
| `environment` | Current environmental record or references to it |
| `outputs` | Path of the product role to the relative running directory |
| `diagnostics` | Statement of actual deficiency, error or partial completion, to provide the next step |

The list of items is available by field. Unknown information is clearly missing and the old records are read by actual source. The helper and the follow-up tool read the list and find the results.

### Functional update and human review

Equivalence under established targets is routinely repaired, collated, and completed by the project assistant within the existing mandate, delivering the basis for actual behaviour and inspection.

| Trigger condition | Decision requiring clarification |
| --- | --- |
| Study of changes in indicators, data ranges, samples, weights or numerical strategies, impacting conclusions or historical comparability | Presentation of representative pre- and post-representation results, indicating whether old results can be replicated and recosted |
| Public access, results format or directory changes affect existing users | Listing of affected callers, relocations or compatibility options |
| Changes in costing, time, external publication or authority that must be determined by humans | Description of specific scope, budget, options and expected consequences |
| Changes in the common agreement will change the working methods of other projects | Give a first-line case, proposed changes, application of projects and transition modalities |

The review material is based on a sample of actual objects or representatives and consists of current behaviour, proposed behaviour, evidence, options and recommendations. The decision has been taken to provide feedback on the project or the actual responsible document, which will be followed.

### Project implementation and joint update

In the same description, the access project registers the use of the version, catalogue map, running and testing portal, precheck and performance budget, environmental sources, results list, and exceptions. Clearly, there are provisions to be implemented, so that planning is not considered to be an existing capacity. Skills are used to implement specific work, and the facts, causes and effects of the project are fed back into the project. Reusable improvements are returned to this agreement or to the responsible module. The current protocol is implemented by the project assistant on a document basis, and machine aggregation and automatic check takes effect after access to the actual list.

<a id="project-documentation"></a>

## Item documents

### Writing

The course gives examples of what can be followed, the operating guide writes the prerequisites, steps and expected results, the reference page lists the actual interfaces, default values and limits, and the rationale explains the concepts and conditions of application. The project is organized using the existing directory. [Diátaxis](https://www.diataxis.fr/)]

Explains the meaning when the abbreviation appears first. The same thing keeps the exact spelling on the relevant page with the same word, the public command and the configuration key. Titles write directly to the objects to be checked by the reader or the actions to be performed. Use the common words in the current project and field. Open interfaces mark and explain by the original name, while other titles and text are named by the object. [Google Developer's Word Guide](https://developers.google.com/style/word-list)]

Execute the environment page to distinguish between the installation requirements and the software, version and resources that are actually in operation. Use existing configurations, environmental lists, code versions or original results to refer directly to them; describe the extent to which they can be checked if missing. [The Turing Way: Recoverable environment](https://book.the-turing-way.org/reproducible-research/renv/)]

### How to find and update the document

Root README writes first about the project's own installation steps, data and environmental selection, key running commands, and product portals. Using ResearchHarness, a separate optional access description describes shared skills, resource bindings, and structural results, and writes the path of the machine as an example of current access.

From root README into `doc/README.md`. Index by item map the first level of the directory, with a description of the capabilities provided by the directory, to whom to use it and to whom to enter it. Data sets, models, tasks, configurations and experiments use the fixed page below. Each fact has a maintenance location and other pages point to it. The whole project maintains the corresponding page of `doc/` for which the current description is assigned. Checks the actual function of each level of the directory and applies the page according to the type of item. The actual function is covered by the original or input, build and use, test and acceptance statement of the work or tool type.

| Location | What can a reader find? |
| --- | --- |
| `doc/README.md` | Use of the document itself, first-level catalogue mapping, knowledge, environment, source code and laboratory entry. |
| `doc/datasets.md`、`doc/models.md`、`doc/tasks.md` | Components and their conditions of use. |
| `doc/conf.md` | Parameters control behaviour, current default and coverage in practice. |
| `doc/experiment.md` | Article-by-article pilot reports based on actual operations and available results. |
| Pages of the actual first-level directories `doc/base.md`, `doc/tests.md`, `doc/scripts.md`, `doc/third_party.md` | The base layer covers the matching of the main package, and the actual path is indexed. |
| `doc/environment/README.md` | Environmental access is required. Direct links from the document index cover the interpreter, dependency on installation, equipment and data preparation, light validation and the recording position of the operational environment. |
| `doc/knowledge/`、`doc/code/` | The project terminologies and scientific knowledge, source structure and project description. The directories use README navigation. |

All tier 1 directories with project responsibilities are described, including master packages, project skills and optional directories. Temporary caches, version control metadata and automatically generated subdirectories are grouped according to the tools or product pages to which they belong. Descriptions and indexes are added at the same time as the directories are enabled. The navigation is updated as it is removed or merged, and historical references retain its source.


### Description of the base and other level I directories

The document index uses a short link to the corresponding page. The base level describes how the document is actually synthesized and distributed, the test description is how it is implemented and what is covered, the foot note is run by whom and its output, the source, version, licence and actual user of the external asset, and the data root describes the preparation and search conditions.

### Writing and cross-checking each item

The entry can be added, rewrited, split, merged or subtracted. The common description is placed at the top, the specific members write the use, the selection conditions and the difference that can be observed. The synonym entry is placed in the same entry, the search mode is maintained. The realization or the study calibration changes with the maintenance of the module and the retention of the original intent of the historical record.

The data set description is based on the data source, with a famous subset describing the scope, classification or filtering conditions and the applicable tasks. The model is organized according to the family and the variable organization of the actual choice, with the shared structure placed under the family or series. The task is organized according to the work to be performed, the subtask is written under the task to be performed, indicating the direct call, the input received or the last product, and the results for the next use. The independent entry can refer to the same subtask, share a centralized description of the operation and a link to the task from which it is used.

The papers, official model cards and data sets describe additional background and sources, local registration, public configuration, consumer and product decisions on the actual input, default behaviour, compatibility and outcome of the project. The links are used to verify and extend reading. When evidence is not available, the missing information and the judgement affected is written. The completed checklist checkes the coverage, and the reader is asked whether the body is able to answer the actual use of the information independently.

The data description may draw on [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)] sources, composition, processing and uses. Model notes may draw on [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) conditions and limitations of use.

### Reference Notes and Chapter Levels

When referring to documents, profiles, or other information, the purpose, scope of application, main function of the information presented by the source, and an understandable example of what the reader can find in it. Repeated references can point to the description already written on this page. Key notes are read independently. Parameters write default values, conditions of entry and effects of modifications. Task pages refer to the basis and limits for the selection of data and models. The data and model pages are clear of the basis and limits for selection. The test report is based on the main results, comparative conditions and limitations. After the corresponding facts are quoted, they are available for verification or details. The pure index can be used as an entry point for one or two sentences of summaries, and the table of contents can be found in a table of contents.

Longer documents can be used for `1`, `1.1`, `1.1.1`. Titles and references are still subject names. A short page can use a meaningful title. The document directory corresponds to the actual file function and avoids the introduction of a further category name for the same structure. The configuration page is organized by the project ' s file structure and the associated shared settings are grouped in one place. The task parameters for different applications or entry conditions are listed, and the key name, default value, unit or optional value, applicable condition and modified effects are written. The historical key and the internal field specified by the formula indicate its role.

### Fixed Format for Component Pages

The three pages use the three sections of the Common Parameters for Use and Entry. The Common Parameters point to the three sections. `doc/conf.md`,The component entry supplements the actual difference. Each component has a subheading with a public identifier, which is then explained in order.**Function, method of selection, input and product, proprietary parameters, basis of certification**.Validation is based on links to consumers, regression checks or representatives, with an indication of the scope of application.

| Page | It's specific to each one of them. |
| --- | --- |
| Data Set | Data sources, samples and labels, classification and preparation modalities, mandate constraints. |
| Model | Series or variant, construction, input output, weight source and applicable combination. |
| Tasks | Available data and models, operating models, calibration and calibration of indicators, and how the results are readable. |

### Fixed format for parameter pages

`doc/conf.md` Starts with normal commands, default combinations, overlays, and where to read effective values. The text follows the actual configuration directories and files. Each file has a small section that corresponds to the only configuration file of the configuration branch, describing the purpose, parameter meaning, default values, optional values, effective conditions, overlaying, incognito and compatibility by the name section of the document. Positions the public selection with a full key name; synonyms and matching aliases can be combined. Fixed or derivative behaviour is written in the responsible task or component entry. Using examples of values that change the result, a table can be used to find the entry.

When a project uses a file configuration, automatically synchronizes the navigation, current values and directly readable default values from the actual file. The configuration changes both the meaning of the study and the use of the parameter. Submit, continuously integrate and deploy the verification of the configuration path attribution and document synchronization.

Runs the directory saver ' s configuration at the time it takes effect. When the current parameter document is updated, you interpret the old results from the effective configuration and version of the old experiment.

When new, removed or modified public parameters are added, [maintain-conf](../../../.agents/skills/maintain-conf/SKILL.md) is used to check actual consumer and behavioural changes, to update current defaults, cover conditions and affected old usages, and to synchronize to the parameter page in accordance with this section.

### Fixed format of the experimental report

`doc/experiment.md` Each article is headed by the name of the experiment and has five in the following order. Repeated attempts can be grouped under the same article, identifying each one. Only actual attempts to explore, run or specifically block access to the report.

1. **Purpose and judgement**.A description of the questions to be answered, the subject to be compared and how to judge the results.
2. **Operation and Conditions**.Lists options for operational identifiers, datasets and disaggregation, models and weights, tasks, actual scope and re-emergence of impacts. Link effective configuration, implementation environment and operation list.
3. **Status and products**.Records the actual state of success, partial completion, failure, blocking or cessation, linked products, key indicators, and access. The indicator indicates the unit or calibration and coverage..
4. **Conclusions and uses**.Indicate what can be answered on the basis of the results, and which steps can be taken to implement them.
5. **Limitations and follow-up**.Description of missing items, comparable conditions, follow-up verification or matters to be decided upon by mankind.

Lists, logs, originals, and detailed reports generated with a single operation are left in the operating directory. The cross-practice conclusions and the body of human experiments are summarized by `doc/experiment.md`, long-standing research protocols, methodological descriptions and concepts are assigned to the mission document or `doc/knowledge/` by their actual use. When there is a large number of independent people who write reports that cannot be carried over by a single operation, the page can be removed by real theme, and the index should show the actual readers and uses of the new directory.

When running, searching or reviewing the experiment, acquire the effective configuration and readable product from the project entrance with [maintain-experation](../../../.agents/skills/maintain-experiment/SKILL.md) to update the corresponding actual test entries in this section.

### Knowledge, implementation environment and source structure

- **Knowledge**.From `doc/knowledge/README.md` Checks scientific concepts, terminologies and research bases. Each entry that requires an independent explanation has a name and aliases, definitions, conditions applicable in the project, sources and associated experiments or codes..
- The ** operating environment **. The `doc/environment/README.md` searchable environment and its uses, interpreter, source and installation, equipment requirements, data and routing, and how to confirm which environment is actually used.
- **Source Structure**.From `doc/code/README.md` Enter `extract-structure` When you request a structure, you will determine the root, scope and version of the project and press the available skills entry for the project. `extract-structure` generating;place long-reading structural descriptions or stable links `doc/code/`,Mark range, source version, date of generation and application. Synchronize access and description when a directory or key call relationship changes. The results are maintained in the source version and updated as necessary for actual reading. The matching program and temporary product are saved according to skills own rules..

### Update and deliver to humanity as it is achieved

The document index is used to locate the item that is to be read or updated. The researcher determines how to run through the component pages and the parameter pages, and interprets and supports it by keeping records and reporting on the status and conclusions, and by checking the relevant knowledge, environment and structure pages. The calibration or action to be chosen by humans is accompanied by corresponding pages and evidence; the identified usage, terminology or conclusions are returned to the responsible page for follow-up.

- **On maintenance**,You can use the same changes as you do when you find the affected page from the actual entry, configuration, consumer and product. [maintain-optional](../../../.agents/skills/maintain-optional/SKILL.md) Update of these assets and access to affected projects in line with actual use.
- **During the review**,Checks public options, default values, examples, input outputs and results links. [maintain-code](../../../.agents/skills/maintain-code/SKILL.md) Review the true usage to determine which operations are affected and synchronize the repair of the code and document within the authorization.
- **At reporting**,Delivery**Actual functional changes and usage, certification results and conditions of application, compatibility effects or matters to be decided upon**.The detailed running record remains on the appropriate page, reporting the body of the report is based on the current use and judgement of the researcher..
