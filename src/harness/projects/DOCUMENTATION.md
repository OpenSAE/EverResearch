# Scientific project documentation and maintenance reporting

## Purpose

Provides for how research projects concentrate their use instructions, knowledge, environment, source structure and experimental reports on the project `doc/` to enable researchers to understand the functionality, use the results and review the maintenance basis.

## Scope

When you first approach other layouts, you find the existing readers, access points, and the equivalent documents, and then you set the corresponding in this range. Here you keep the general rules, specifying, data, and experimental facts, to be kept in the respective project.

## Writing

The course gives examples of what can be followed, the operating guide writes the prerequisites, steps and expected results, the reference page lists the actual interfaces, default values and limits, and the rationale explains the concepts and conditions of application. The project is organized using the existing directory. [Diátaxis](https://www.diataxis.fr/)]

Explains the meaning when the abbreviation appears first. The same thing keeps the exact spelling on the relevant page with the same word, the public command and the configuration key. Titles write directly to the objects to be checked by the reader or the actions to be performed. Use the common words in the current project and field. Open interfaces mark and explain by the original name, while other titles and text are named by the object. [Google Developer's Word Guide](https://developers.google.com/style/word-list)]

Execute the environment page to distinguish between the installation requirements and the software, version and resources that are actually in operation. Use existing configurations, environmental lists, code versions or original results to refer directly to them; describe the extent to which they can be checked if missing. [The Turing Way: Recoverable environment](https://book.the-turing-way.org/reproducible-research/renv/)]

## How to find and update the document

Root README writes first about the project's own installation steps, data and environmental selection, key running commands, and product portals. Using ResearchHarness, a separate optional access description describes shared skills, resource bindings, and structural results, and writes the path of the machine as an example of current access.

From root README into `doc/README.md`. Index by item map the first level of the directory, with a description of the capabilities provided by the directory, to whom to use it and to whom to enter it. Data sets, models, tasks, configurations and experiments use the fixed page below. Each fact has a maintenance location and other pages point to it. The whole project maintains the corresponding page of `doc/` for which the current description is assigned. Checks the actual function of each level of the directory and applies the page according to the type of item. The actual function is covered by the original or input, build and use, test and acceptance statement of the work or tool type.

| Location | What can a reader find? |
| --- | --- |
| `doc/README.md` | Use of the document itself, first-level catalogue mapping, knowledge, environment, source code and laboratory entry. |
| `doc/datasets.md`、`doc/models.md`、`doc/tasks.md` | Components and their conditions of use. |
| `doc/conf.md` | Parameters control behaviour, current default and coverage in practice. |
| `doc/experiment.md` | Article-by-article experimental reports based on actual operations and available results. |
| Pages of the actual first-level directories `doc/base.md`, `doc/tests.md`, `doc/scripts.md`, `doc/third_party.md` | The base layer covers the matching of the main package, and the actual path is indexed. |
| `doc/environment/README.md` | Environmental access is required. Direct links from the document index cover the interpreter, relying on installation, equipment and data preparation, light validation and the recording position of the operational environment. |
| `doc/knowledge/`、`doc/code/` | The project terminologies and scientific knowledge, source structure and project description. The directories use README navigation. |

All tier 1 directories with project responsibilities are described, including data roots, master packages, project skills and optional directories. Temporary caches, version control metadata and automatically generated subdirectories are grouped according to the tools or product pages to which they belong. Descriptions and indexes are added to the directory when it is enabled. The navigation is updated with the same time when removed or merged, and historical references retain their source.

When establishing an index or adjusting a level I catalogue map, check [the catalogue of scientific projects and the document function](LAYOUT.md) to determine the function to be described in the document from the actual directory attribution, conditions of access and call relationships.

## Description of the base and other level I directories

The document index uses a short link to the corresponding page. The base level describes how the document is actually synthesized and distributed, the test description is how it is implemented and what is covered, the foot note is run by whom and its output, the source, version, licence and actual user of the external asset, and the data root describes the preparation and search conditions.

## Writing and cross-checking each item

The entry can be added, rewrited, split, merged or subtracted. The common description is placed at the top, the specific members write the use, the selection conditions and the difference that can be observed. The synonym entry is placed in the same entry, the search mode is maintained. When the calibration of the accomplishment or study changes, the maintenance is done with the module and the original intent of the historical record is maintained.

The data set description is based on the data source, with a famous subset describing the scope, classification or filtering conditions and the applicable tasks. The model is organized according to the family and the variable organization of the actual choice, with the shared structure placed under the family or series. The task is organized according to the work to be performed, the sub-task is written under the task to be performed, indicating the direct call, the input received or the last product, and the results for the next use. The independent entry can refer to the same sub-task, share a centralized description of the operation and a link to the task from which it is used.

The papers, official model cards and data sets describe additional background and sources, local registration, public configuration, consumer and product decisions on the actual input, default behaviour, compatibility and outcome of the project. The links are used to verify and extend reading. When evidence is not available, the missing information and the judgement affected is written. The completed checklist checkes the coverage, and the reader is asked whether the body is able to answer the actual use of the information independently.

The data description may draw on [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)] sources, composition, processing and uses. Model notes may draw on [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) conditions and limitations of use.

## Reference Notes and Chapter Levels

When referring to documents, profiles, or other information, the purpose, scope of application, main function of the information presented by the source, and an understandable example of what the reader can find in it. Repeated references can point to the description already written on this page. Key notes are read independently. Parameters write default values, conditions of entry and effects of modifications. Task pages refer to the basis and limits for the selection of data and models. The data and model pages are clear of the basis and limits for selection. The test report is based on the main results, comparative conditions and limitations. After the corresponding facts are quoted, they are available for verification or details. The pure index can be used as an entry point for one or two sentences of summaries, and the table of contents can be found in a table of contents.

Longer documents can be used for `1`, `1.1`, `1.1.1`. Titles and references are still subject names. A short page can use a meaningful title. The document directory corresponds to the actual file function and avoids the introduction of a further category name for the same structure. The configuration page is organized by the project ' s file structure and the associated shared settings are grouped in one place. The task parameters for different applications or entry conditions are listed, and the key name, default value, unit or optional value, applicable condition and modified effects are written. The historical key and the internal field specified by the formula indicate its role.

## Fixed Format for Component Pages

The three pages use the three sections of the Common Parameters for Use and Entry. The Common Parameters point to the three sections. `doc/conf.md`,The component entry supplements the actual difference. Each component has a subheading with a public identifier, which is then explained in order.**Function, method of selection, input and product, proprietary parameters, basis of certification**.Validation is based on links to consumers, regression checks or representatives, with an indication of the scope of application.

| Page | It's specific to each one of them. |
| --- | --- |
| Data Set | Data sources, samples and labels, classification and preparation modalities, mandate constraints. |
| Model | Series or variant, construction, input output, weight source and applicable combination. |
| Tasks | Available data and models, operating models, calibration and calibration of indicators, and how the results are readable. |

## Fixed format for parameter pages

`doc/conf.md` Starts with normal commands, default combinations, overlays, and where to read effective values. The text follows the actual configuration directories and files. Each file has a small section that corresponds to the only configuration file of the configuration branch, describing the purpose, parameter meaning, default values, optional values, effective conditions, overlaying, incognito and compatibility by the name section of the document. Positions the public selection with a full key name; synonyms and matching aliases can be combined. Fixed or derivative behaviour is written in the responsible task or component entry. Using examples of values that change the result, a table can be used to find the entry.

When a project uses a file configuration, automatically synchronizes the navigation, current values and directly readable default values from the actual file. The configuration changes both the meaning of the study and the use of the parameter. Submit, continuously integrate and deploy the verification of the configuration path attribution and document synchronization.

Runs the directory saver ' s configuration at the time it takes effect. When the current parameter document is updated, you interpret the old results from the effective configuration and version of the old experiment.

When new, removed or modified public parameters are added, [maintain-conf](../../../.agents/skills/maintain-conf/SKILL.md) is used to check actual consumer and behavioural changes, to update current defaults, cover conditions and affected old usages, and to synchronize to the parameter page in accordance with this section.

## Fixed format of the experimental report

`doc/experiment.md` Each article is headed by the name of the experiment and has five in the following order. Repeated attempts can be grouped under the same article, identifying each one. Only actual attempts to explore, run or specifically block access to the report.

1. **Purpose and judgement**.A description of the questions to be answered, the subject to be compared and how to judge the results.
2. **Operation and Conditions**.Lists the options for operational identifiers, datasets and disaggregation, models and weights, tasks, actual scope and re-emergence of impacts.
3. **Status and products**.Records the actual state of success, partial completion, failure, blocking or cessation, linked products, key indicators, and access. The indicator indicates the unit or calibration and coverage.
4. **Conclusions and uses**.Indicate what can be answered on the basis of the results, and which steps can be taken to implement them.
5. **Limitations and follow-up**.Description of missing items, comparable conditions, follow-up verification or matters to be decided upon by mankind.

Lists, logs, originals, and detailed reports generated with a single operation are left in the operating directory. The cross-practice conclusions and the body of human experiments are summarized in `doc/experiment.md`, long-standing research protocols, methodological descriptions and concepts are assigned to the mission document or `doc/knowledge/` by their actual use. When there is a large number of independent people writing reports that cannot be carried over by a single operation, the page can be removed by the real subject, and the index should show the actual reader and the purpose of the new directory.

When running, searching or reviewing the experiment, acquire the effective configuration and readable product from the project entrance with [maintain-experation](../../../.agents/skills/maintain-experiment/SKILL.md) to update the corresponding actual test entries in this section.

## Knowledge, implementation environment and source structure

- **Knowledge**.From `doc/knowledge/README.md` Checks scientific concepts, terminologies and research bases. Each entry that requires an independent explanation has a name and aliases, definitions, conditions applicable in the project, sources and associated experiments or codes.
- The **operating environment**. The `doc/environment/README.md` searchable environment and its uses, interpreter, source and installation, equipment requirements, data and routing, and how to confirm which environment is actually used.
- **Source Structure**.From `doc/code/README.md` Enter `extract-structure` When you request a structure, you will determine the root, scope and version of the project and press the available skills entry for the project. `extract-structure` generating;place long-reading structural descriptions or stable links `doc/code/`,Mark range, source version, date of generation and application. Synchronize access and description when a directory or key call relationship changes. The results are maintained in the source version and updated as necessary for actual reading. The matching program and temporary product are saved according to skills own rules.

## Update and deliver to humanity as it is achieved

The document index is used to locate the item that is to be read or updated. The researcher determines how to run through the component pages and the parameter pages, and interprets and supports it by keeping records and reporting on the status and conclusions, and by checking the relevant knowledge, environment and structure pages. The calibration or action to be chosen by humans is accompanied by corresponding pages and evidence; the identified usage, terminology or conclusions are returned to the responsible page for follow-up.

- **On maintenance**,You can use the same changes as you do when you find the affected page from the actual entry, configuration, consumer and product. [maintain-optional](../../../.agents/skills/maintain-optional/SKILL.md) Update of these assets and access to affected projects in line with actual use.
- **During the review**,Checks public options, default values, examples, input outputs and results links. [maintain-code](../../../.agents/skills/maintain-code/SKILL.md) Review the true usage to determine which operations are affected and synchronize the repair of the code and document within the authorization.
- **At reporting**,Delivery**Actual functional changes and usage, certification results and conditions of application, compatibility effects or matters to be decided upon**.The detailed running record remains on the appropriate page, reporting the body of the report is based on the current use and judgement of the researcher.
