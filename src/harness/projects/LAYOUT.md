# Catalogue of research projects and documentation functions

## Purpose

The first-level layout of the scientific project, the conditions for the operation of the second-tier directories, the attribution of documents, the naming rules and the call relationship.

## Scope

The CUB classification template provides examples of layouts with operational accesses, components and results.

## 1. Overall layout and necessity

When accessing a strange project, a whole combo catalogue or reconnecting multiple components, use [maintain-project](../../../.agents/skills/maintain-project/SKILL.md) to identify responsibilities from the real entrance, organize specialized maintenance and check the modified use links.

The following table shows the functions of the root list of the project. Each scientific project has an entity-level catalogue `base/`, `datasets/`, `models/`, `tasks/`, `conf/`. The total acceptance is `rh projects project check <project-root>`, which contains a detailed tree-wide path check. `rh projects layout check <project-root>` is referred back to the physical tree and reports the path and non-compliance terms. The whole project acceptance is based on the withdrawal status `0`. The specific path and documentation rules are implemented by `src/harness/core/layout.py`.

| Location | Required level of preparedness | For what? |
| --- | --- | --- |
| root directory `README.md`, `AGENTS.md` | Yes, sir. | The former describes the purpose of the project, the entry point for normal operations and the location of the results, while the latter describes the maintenance of the rules within the project and locates the common agreement. |
| `conf/` | Yes, sir. | Provides `conf/config.<format>` for official access and effective formulations. |
| `datasets/` | Yes, sir. | At least one actual data set and its reading, preparation or disaggregation is achieved. |
| `models/` | Yes, sir. | At least one actual model and its construction, loading or call realization. |
| `tasks/` | Yes, sir. | There is at least one actual scientific mission, with an additional `precheck/` to provide an automatic precheck for a formal mission. |
| Data Roots | If you have the appropriate input, you must have it. | Default `data/`, can register the actual location or specify when running. |
| `experiment/` | When there's a scientific operation. | A fixed list of experimental products under the root directory. The running entrance is located from the root of the project and automatically created when you write it first. |
| `base/` | Yes, sir. | Saves real open access, configuration synthesis, component selection, task distribution and common running support. |
| `doc/` | Yes, sir. | From README navigation to document index, a description of the actual level I directories is provided and connects components, parameters, experiments, knowledge, implementation environment and source structure. |
| `tests/`、`scripts/`、`third_party/` | Optional | Automatic regression, manual running tools and third-party source code are established on a practical basis. |
| `assets/` | When resources are retained for a long period | By type of resource and by specific resource group, retain resources, a description of sources and their dedicated scripts. |
| `tmp/` | When there's a one-time project | A list of names is used for each job and ends as intended. |
| `.researchharness/`、`.agents/skills/` | Created when access or skills are available | The former preserves project statements, while the latter are used for skills detection. |

The root directory is used primarily for navigation, installation and access; the component logic, configuration, documentation and running files are each assigned to them. The secondary directory is created only when the corresponding duties actually appear. A small number of files can be flat, the duties specified and then decoded into a generic directory. The project structure describes the actual command, the catalogue map and the open path available to help the assistant to take over by pressing the existing entrance.

The project root name uses two or three words, PascalCase, such as `ContextMemory`, which contains at least one full English word. The self-defined directory and file name contains at least one full English word, giving preference to a word named sub-task, with multiple words separated by underlined. Real models, data sets and their versions can be distinguished by numbers. The directory of these components in the configuration mirrors follows the same place. The file, the external resource content and the executing identity in the running records specified in the framework follow the same format. The tree-wide examination reports on the project root name, numbers and vocabulary problems.

The code checks to overwrite the visible project content. The hidden path and Python byte-code caches are left to their respective tools. The checker reads the experimental identity from the actual project component directory and the component directory map of the main configuration `conf/config.<format>` and checks the configuration from the actual source directory. The function is whether the project is actually enabled, the path corresponding code is actually called, and whether the same functionality can be combined and validated along the normal entry.

## 2. Base layer and scientific components

Command access, open interface, movement control, and general operating codes to enter `base/`, sample and classification to enter `datasets/`, model structure and reasoning to enter `models/`, training, assessment, laboratory computing, and mission-specific indicators to enter `tasks/`. Installations can still be left through packaged maps or thin entrances, and original public import can point to after-dismantling.

The central inspection requires five entity directories, `base/` entrances or operational realizations, `conf/` configuration portals, and real source codes for data sets, models, official missions. Empty directories, slots, registrations and pre-screens alone cannot function as components. Check `base/` embedded component source trees and limit direct documentation to 15 per layer at `base/`, `tasks/`, `scripts/`, `tests/` and identifiable old source root. `datasets/` and `models/` sub-tree waivers remain to be checked.

When there are more than 15 direct subdirectories, `project check` reports the path, number of files and number of subdirectories by `directory_reviews` for functional inspection and repair. The independent functions in the existing directory are based on actual calls. The number of documents remains at the mandatory limit of 15.

The central structure checks the disk and the actual call evidence that the components have been correctly connected.

| Level 2 directories or files | Enable Conditions | Documentation duties and access rules |
| --- | --- | --- |
| `commands.py`, `__main__.py` or equivalent entry in `base/` | When ordered | Parsing parameters, selecting actions, showing results or malfunctions. Command lines and other callers revert to the responsible module. |
| `base/` Medium `runtime/` | When supported by project-level running | Runrs call for data, models and tasks. Path resolution, configuration synthesis, operating environment and records are organized according to their actual duties. `paths.py`, `config.py`, `runtime.py` and `records.py` are the filenames that can be used to assume the corresponding duties. The CUB template is `base/cub_template/runtime/`. |
| `base/` Medium `interfaces/` | When there's a steady external call | The entry indicates input, return value, failure condition and compatibility range. |
| `plugins.py` and `registry.py` for the base level under each component directory | When multiple components need to be individually configured | The various components directories maintain a login to the entry point. |

### Standard catalogue for three types of components

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
    ├── gate.py                   precheck call for a formal task
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
| Tasks | Receive configuration and selected components, complete training, assess or analyse and deliver indicators and results | The precheck uses the same component and mission step, and the public operating module records configuration, environment, state and product location. |

Configures the selected components by using the only entry for the project. The existing items can be used for registration or selection. When separate components are added, the component realization, registration and formulation are added, and the general command, precheck and running records continue to be used along the existing interfaces. Available options are given when searching for the unknown identifier, and the original identification and formulation are publicly available.

The components examine the parameters they have, the tasks check whether the selected data and models can be implemented together, and the public operating modules call for them before actually loading the resources. Task-specific indicators, measurements and report syntax are maintained. A mission can be trained, analysed or evaluated under the same objective of the sub-mission. Sub-mission declarations are entered, exported and called, and the public inspection and results are coordinated by the task to which they belong. The common operation of the individual and long-term caller is placed in a position of actual responsibility and is called by multiple tasks.

Template `cub200` and `synthetic` Intersection using the same disaggregated data,`resnet18_mlp` and `small_cnn` It's all possible. `classification` Select. The master configuration uses Hydra Configure Group Independent Selection Component. `tasks/precheck/` The time, baseline bottlenecks, and candidates are compared. `tasks/precheck/`,The operational module provides the public equipment to synchronize and save access to the fixed sample view.

## 3. Configure and relative paths

When a layering is used, the parameter prefix represents the actual owner. Each subtape under the task has its own prefix, and the shared setting is maintained by the task or cross-tape in a uniform operating layer. Output values, such as output identity and path, are generated from the operating layer and the specific study combination is saved by the experimental formulation.

`conf/` organises a default set of project configurations. The reference template is used `conf/config.yaml` in a single format, and the default parameters and optional component definitions are centralized in this file. The configuration of the specific experiment is kept as it runs at `experiment/`, README gives the official access and coverage.

| Configure Paths | When will it be used? | Save Contents |
| --- | --- | --- |
| `conf/config.yaml` | When the project adopts the unified configuration portal | Default component combinations and shared defaults, loaded by the normal entry. |
| `conf/<relative-source-directory>/` | When data, models, tasks or running components are actually readable configurations | The relative directory where the responsible source code is located is taken from the root of the item and the two-stage path is maintained under `conf/`. For example `tasks/capture/` corresponds to `conf/tasks/capture/`. |
| Responsible for running the configuration directories of the modules | When the environment, device or path needs to be configured independently | The interpreter, device or the configuration of the input path is placed in the directory that actually loads and validates their operating module. |

Up to two-tier directories under `conf/`. Each configuration branch has one file. Deeper duties are combined into a named section of the corresponding file. For example, `conf/tasks/capture/task.yaml` also saves default values, batches and filters for capture tasks, with each entry reading the respective section.

The configuration of new, modified, moved, removed and deployed must check the source code and configuration path and verify that it is loaded. Check the submission, continuous integration and release of access items. The configuration changes are automatically synchronized to `doc/conf.md`, indicating that the semantics in the description are maintained with the code.

When adding, removing or modifying the open parameters, cross-checking the configuration file attribution and document synchronization with [maintain-conf](../../../.agents/skills/maintain-conf/SKILL.md) for actual consumer processing parameters syntax, default values, overlaying and compatibility.

The project entrance determines the root of the project, and the base layer analyzes the default configuration, the project data and the agreed starting point `experiment/`.The component receives the actual path. The path within the new formulation defaults against the project root. A formulation already exists that follows clear relative rules of the configuration file, for example CUB Data path relative to the formula directory. README Defines where the command line path and the formula path start, respectively. Python Give it to the project by means of a named binding, parameter or environment variable.

[Project access and in-house resources](../core/PROJECT.md)Description of how multiple projects are placed in parallel with shared data in the parent area, applicable to arrange parent directories, register items and bind resources.

## 4. Testing, description, manual tools and third-party information

The source station that needs to be built by the document tool is located `doc/code/<Name Document Station>/`.Site directory to save build entrances Makefile,make.bat and requirements.txt,Build input in `source/`,Keeps the internal file name, cross-reference and static resource address used in the document tool. Syncs the open build or deployment portal. Generates pages to save for their delivery or cache uses.

[Scientific project documentation and maintenance reporting](DOCUMENTATION.md)Sets the document index, the format of the pages and the basis for their use, which applies to the creation of the project document, synchronized realization, review and experimental reports.

| Level 2 directories or files | When will it be used? | Save content and boundary |
| --- | --- | --- |
| `tests/test_<behavior>.py`、`tests/product/` | When functional behaviour requires continuous review | A small number returns to the root layer, forming a group of continuously maintained products and then returning. `product/`.Filename locates actual behaviour or entry. |
| `tests/integration/` | When there is an independent cross-component, real service or environmental link check | (b) Maintain chain testing, with an indication of operating conditions, actual resources and coverage. |
| `tests/fixtures/` | When multiple groups test the same small sample | Keep a description of the small fixed input, the expected results and the source of the need. |
| `doc/code/` | Project document portal | Navigate to `extract-structure`, the project structure results and their source version. Examples of architecture, interfaces, transfer of components and projects are here. |
| `doc/knowledge/` | Project document portal | (d) Preservation of scientific concepts, terminology, interpretation, basis of agreement with the project, citing actual sources. |
| `doc/environment/README.md` | Required by `doc/README.md` link | Saves relying, interpreter, equipment requirements, operational readiness and light authentication methods. The physical environment is read from the corresponding run records. |
| `scripts/examples/`、`scripts/release/` | When there is an independent presentation or release operation | The demonstration and distribution portals are named for each purpose and the thin scripts are formally called. |
| `scripts/<purpose>/` | When another group of operations has a clear user | Saves the instructions, access and necessary configurations by use. The calculation has been re-used for the official task and is moved to the responsible module. |
| `assets/<asset-type>/<asset-name>/` | When resources are retained for a long period | Recording uses, sources and updates with `README.md`, preserving resources with `files/`, and preserving resources with `scripts/`. |
| `third_party/<upstream-name>/` | When a third party source is actually retained | The location of the upstream project management package, where the upstream physical path and file name are maintained. |

`tests/` is optional, and the actual change check is selected by [the maintenance inspection rules of the project agreement](PROTOCOL.md#file-function-and-maintenance-check). When the project has a specific precheck, audit or client test, register its real entry and existing grouping.

The script directory is organized according to the user's operating organization. Multiple entry points perform the same job and maintain the same entry when differences can be expressed by name parameters. Project documents describe the official components to be called at each entry, the type of input to be entered and the way to view the results.

## 5. Data, operation and access information

| Location | Enable Conditions | Documentation responsibilities |
| --- | --- | --- |
| `data/<dataset-name>/<version>` or registered outside location | When there's a real input | Positioning data, labels, versions and corresponding pre-processing caches. The temporary storage and locking of data preparation follows the data root and the atoms write to the same file system. Project configuration points to the actual root directory and runs the input identity used for record-keeping. |
| Project level `tmp/` | One-time engineering work that cannot be carried out by the existing public entry point or directory | The code, configuration, and document of the other level I directory point to the official document. `maintain-tmp` Review for conversion or clean-up. |
| `experiment/<dataset>/<model>/<task>/<subname>/<optional-role>/` | When the result is generated | `subname` Describes the experiment or the object of exploration in one or three lowercase English terms, under a single underlined word. The subtasks or the name of the experiment under the mission are named according to the actual function, the purpose of the exploration or the key parameters that make up the conditions of the study, and can be grouped as required. Each level provides information that has not been expressed by the superior. The executive layer is only enabled when there is an independent use or control role. Serial numbers, dates, seeds and other parameters are written in the configuration or execution record. Repeated execution of the same use and role is distinguished by the list. |
| `experiment/<dataset>/<task>/<experiment-name>/<optional-role>/` | When studying the calculation directly to the data | This type of operation saves the model layer. |
| One run `config.yaml` or the configuration format used for the item | Configure successfully after parsing | Saves the configuration with the default, selected components and overwhelms. The running list points to the file. |
| One run `metadata/` | When a run result to be handed over | The `manifest.json` is the default reading portal, which can register the equivalent path. Configure, precheck back, place the environment record here or quote from the list. |
| One run `reports/`, `logs/`, `artifacts/`, `tmp/` | When corresponding output is available | Readable reports, process logs, usable products, and temporary materials are assigned separately. |
| `assets/history_experiment/<named-result>/` | Keep existing experiments or demonstrations | The operation that you leave at `experiment/` must be checked for identity, effective configuration and product. |
| `.researchharness/project.yaml`、`.researchharness/central.json` | When using the respective access function | The project is subject to a central project order. |
| `.agents/skills/<skill-name>/` | When there are projects or skills-sharing | Each skill provides `SKILL.md`. The project maintains its own skills, which are centrally shared and accessible by a project switch. |

Component identification, catalog and Python files are used in lowcase English to describe their use, and multiple words are underlined. Formal interfaces and upstream original names are used in original form. Time and attempt numbers are used to run identity and archive. The new directory indicates the conditions under which they are enabled, the actual caller and the corresponding entry, and is synchronized with the protocol [the example of the layout of the reference item](template/doc/code/development/layout.md) to compare the changes to the project catalogue and additions.

The project allows a stable match between the public component identifier and the disk spelling. Read the corresponding rules for writing the statement of the oral re-entry project, and run the list to save the actual component identifier. Select the same path from the same component for acceptance.

The data sets and models in the experimental path are functional positions. When the project has a real family and has multiple independent members, you can express the family and members in two segments at that location, such as `<dataset-family>/<cohort>`.

`experiment/` The results of the joint analysis are assigned to the public entry point to the analysis, the path is determined by the actual master data or registered joint input, and the members and sources are kept on the list. `maintain-experiment`.Source data using a registration number can be identified by Queue Name, the list retains the original number and normally writes the same correspondence to read.

`rh projects experiment check <project-root>` Checks the list, configuration, routing and matching of documents to the list in `artifacts/` and `reports/` for formal experiments. The whole project is maintained simultaneously at `rh projects project check <project-root>`. The results include the number of implementations and specific non-compliance paths. The official reading back of the project continues to verify the actual results.

The project's dependency list is placed in the official position, and the interpreter binds and installs the entrance ResearchHarness.Hugging Face Downloads and General Caches By Local Client or `huggingface-maintain` task directory processing. Data conversion results and reusable caches are attributed to the corresponding data root.

## 6. From which project experience are the rules derived

| Project and actual basis | Approach used | Retain Item Selection |
| --- | --- | --- |
| For SAEBase `saebase/registry.py`, `runner.py`, `conf/config.yaml` | The components are configured with the same marking, distributed at the entrance, and the specific components achieve actual behaviour. | Multiple components need to be used in the registration form. A single classification template can be called directly to three components. |
| SAEBase It's... CI,`tests/product/`,`tests/precheck/` and `tests/integration/` | Group by physical check of objects and operating conditions. There are existing CIs that use different groups to locate mission behaviour, precheck and central access checks. | The project is validated on a risk basis and on the basis of available callers, the test catalogue is available and dedicated clusters are established in line with the actual needs of the project. |
| SAEBase `saebase/runtime/experiment_results.py` and Symselect `experiment/symselect/active_run.json` | A fixed result entry is given to the follow-up assistant. The former can read the single operation and product by list, while the latter locates the current trajectory, configuration and reporting. | The additional dimensions of the running directory, the current running index and historical sources are registered by the project. |
| SpatialPheno `tasks/workflows.py`, `conf/workflow/breast_transformer.yaml` and `models/fusion/classifier.py` | The name command locates specific tasks and formulations. | The current workflow configuration can be used when an operation has multiple steps. The effective configuration of the operation is saved with the result. |
| Visual Novel `skills/`, `examples/` and `scripts/validate_repo.py` | The division of responsibilities by actual delivery, the examination of examples of counterpart skills and works, and the protection of their existing discovery pathways. | Skills products can register their own main structure. |

Each rule describes the person responsible, the conditions of access and the access to which it is read, and maintains a shared and long-term value check of multiple actual callers.
