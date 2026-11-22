# Maintenance items by operational category

## Purpose

Helps the project assistant to implement user requirements into the existing document structure.

## Scope

The management paragraphs of Project `AGENTS.md` are linked here. When you are given a job, you can look at the corresponding sections by the type involved; current commands, configurations, running records, and specific skills of the project provide the basis for realization. In the case of an unknown or pending project, existing duties and user authorizations are confirmed on a project-wide maintenance basis.

## How to select the operation after receiving the request

1. ** Determines the user's actual operations and results. ** Finds where the user enters, what inputs, what results should be seen. Finds the person or program that configures, is responsible for achieving and reading the results from the closest current command in README. When an index is maintained, the project first narrows the reading with the entry, change and old evidence.
2. ** Determines how this is done. ** The current parameter is already supported by the current configuration or command. The current component is subject to a change in the component's behaviour. When an individual can be selected, independently entered, or independently called, a named component is added to the responsible directory, and its registration and access is made available. When removing the action, check the person who is still calling the configuration, command, document and result reader.
3. ** Categorize by physical action. ** A request can contain several operations. For example, "downloading a new version of the data and running an existing model" usually includes downloading data, running experiments, entering the data set only when the input format changes, and reconfiguring the project only when there is a long-term need to increase the public selection. Each action confirms its own chapter, the place where it will read and write, the call-in and the expected product.
4. ** Determines the range of deliverables. ** Ordinary tasks follow the existing level I catalogue and the proper drop point. If the required level I catalogue is lacking, use the existing compliance location or registered external resources; the first launch of the standard catalogue and the entire project restructuring is a clearly approved access or structural maintenance.

Record the path that this round will touch and the user changes that already exist. Batch endings compare the path that actually adds, moves, and generates. You can use the current version to control the status and list of files, or you can directly view the known target directory. If you change the body of the document, you can first verify the specific behaviour. If you have a new path, change the name, move or change the operational output, select the corresponding central check. Local layouts are `rh projects layout check`, the whole item is `rh projects project check` or has the authorized `rh projects maintenance`. Common status check results.

<a id="read"></a>

## Reading, investigation and planning

1. When asked by the user about the status, cause or programme, you start with the object you have specified. Read the project description, the relevant entry, the affected document or the outcome, and complete the basis of the actual call.
2. If you need to run a search to answer a failure, you will be able to determine whether it is a read-out, temporary work or a full-time operation with an output, which is handled by the respective category and authorization.
3. Deliver the actual observed facts, the corresponding path and the judgement that remains to be confirmed. When the user requests the document to be delivered, the document is placed in the applicable category, such as a document or a one-time document.

<a id="base"></a>

## Maintenance of public entrances and operating layers

1. When a user changes the command, parameter resolution, configuration synthesis, distribution of components or common storage, this is done from the open entrance to `base/`; it is concerned about scripts, tests or installed commands for the entrance.
2. Generic resolution, resource selection and call sequences are repaired at `base/`. Individual data sets, models or task algorithms are assigned to corresponding components; only actions shared by multiple actual callers refer to the base layer. The root directory entrance is maintained as the current open entry, and the construction of the declaration and relying list remains in place.
3. The routing resolve identifies the user as starting from the root of the project, the command after installation, or the external work directory. The actual configuration source and the target path is checked with the normal entry. The installation of the portal is completed when the statement is installed. The public result interface is changed by checking the readings that are still supported by the existing product and by updating the corresponding description.
4. **Completion Conditions.** The supported access points can still be formally achieved, and the changed information on behaviour and failure can be physically accessed. Tools, caches and operational products are placed in their respective positions of responsibility. `maintain-base`.

<a id="datasets"></a>

## Add, modify or remove datasets to achieve

1. Determines what the request affects first. The place where the data in the same format is replaced is the data binding or running selection; the change to read, label, divide, preprocess or sample field is `datasets/`; only the original file is obtained and processed by data download.
2. In addition to the variable from the same source, take into account the existing preset or subset; when the new input contract is independently selected, add a name to the respective data set location and connect to the existing registration. When the affected tasks or public parameters are updated, group separately. Remove first the tasks, formulations and documents that are still selected.
3. Check the field, shape, identity, label and division that the task actually reads in using a small representative sample. Confirms whether the cache is still applicable when preprocessing or partitioning is modified, rebuilds the corresponding data version on condition and protects the original input.
4. **Completion Conditions.** The expected samples can be selected and read from the existing access and the data sources and versions can be located in sync. `doc/datasets.md` The corresponding entry and the description of the affected configuration. The detailed steps for adding or deleting `maintain-dataset`.

<a id="models"></a>

## Add, modify or remove models

1. The output of the model from the task configuration check for actual construction parameters, weight re-resolution and task reading. Only existing binding or weight paths are used when replacing compatible weights; the congener variable priority re-use constructor; the independent structure or input output contract is the result of a new name model.
2. `models/` for the corresponding family or series of maintenance structures and loads, to update model registrations and public presets as required.
3. Checks the selected variable, the source of the actual weight, and the load results with the official construction or pre-check entry. Take a small batch from the affected task to go forward and check the output of the actual consumption of the task.
4. The ** completion condition. ** normal entrance clearly selects the model, with the right combination having the available output and the reason for incompatibility. Synchronization models describe and change the task and parameter document. Details are `maintain-model`.

<a id="tasks"></a>

## Add, modify or remove tasks and precheck

1. From existing commands to task registration, computing, reporting and follow-up readers. Give priority to expanding a task when a task has been added to an indicator or result field; a task or sub-task can be created for a task that is selected individually and has an independent input output. Shared precheck follows `tasks/precheck/`.
2. The new result is written into the list by the original recorder and registered in the list. The indicator changes the list, the denominator, the rules and the missing values. The procedure and the old results are still read before the output is removed.
3. Checks the selected components, results and readbacks with a minimum of valid input from the regular mission entry. When pre-check access or failure is changed, verify a valid input and a clearly invalid input, confirming that the latter stopped before the official calculation. Direct references are made when the same condition is covered by the available running evidence.
4. **Completion Conditions.** The public entry points are connected to the actual tasks, pre-checks, and the results are read, and the relevant documents describe how the products are run and explained. `maintain-task`.

<a id="conf"></a>

## Modify open configuration or select existing parameters

1. Determines whether the user changes a value for this operation, saves a renewable formulation, or changes the open options, defaults, or meanings that all callers face. A single run uses the existing overwhelming, and the fully reusable formulation is placed in the current configuration; the historical running of the project retains its own effective configuration.
2. Follow the default definition, the order of overwhelming and the actual readout along the public entry point. Open configuration is maintained for the `conf/` branch, with options added only when there is an independent user selection. New parameters are to be followed by defaults and verifications; changes to semantics or removal parameters are to process the formulation and caller that are still in use.
3. Checks the default values and the visible overlays with a configuration preview, existing tests or short prechecks. When it comes to invalid values or old formulations, only the corresponding scenes are added to confirm that the changes are passed to the actual behaviour.
4. **Completion Conditions.** Users can select the required values from the normal entrance and the results of the validity are visible. `doc/conf.md` or the default value, conditions of application and examples of overwhelming on the item page. `maintain-conf`.

<a id="experiment"></a>

## Start, restore or read experiments

1. Read the old results from the list and from the normal read-back command. Prior to restoration, confirm the mission is resilient and check the original configuration, data, models, environment and check point identity.
2. New start-up preselection data, models, tasks, formulations and equipment to check the actual output root, cache, log and operating budget. Start with a formal project command to allow precheck, configuration snapshots and lists to be generated according to the normal process; the official product is returned to `experiment/` with that operation. The pre-conservation operation is clearly to resume processing along the original entry as it continues.
3. Checks the status, pre-check checkback or log if you fail. Missing data, configuration is invalid and error is transferred to the corresponding category for recovery from the original entrance. Use the normal read-back command to confirm the operation and effective configuration to which the output belongs.
4. **Completion Conditions.** A short certification indicates only the work it actually covers; the formal conclusion is based on the corresponding operational evidence. `maintain-experiment`.

<a id="publishing"></a>

## Publish Item to GitHub

Online maintenance default from `github-publish` The original installation, construction and testing portal of the project is still available for release of a copy., GitHub Release Profiles on Project Roots `.github/`.Two modes of publication[Project release rules](README.md#project-publishing)Whichever applies to the selection of the release entrance or the migration for which the release process is in place.

<a id="tests-scripts"></a>

## Preparation of tests or supporting scripts and decision to retain them

1. See ** for off-the-shelf usage. ** for pre-recovering target behaviour with current project testing, formal command or approved configuration precheck. There is already a case to expand this use when only one input or assertion is missing.
2. ** Writes to the corresponding location by use. ** Auto-returns are found in the existing `tests/` test framework; individual manual batch or export commands are placed at `scripts/`; a one-time comparison is placed at `tmp/<purpose>/`. Scripts return to the official module to test the entry of a small sample of the project or the folder of the actual reuser. The test generated file is completed by the temporary directory of the test tool and the agreed end of the project.
3. **Retention decision after run.** The logic of the formal function is moved to its responsibility. `base/`,`datasets/`,`models/` or `tasks/`,The minimum assertion that this failure or the protection of public behaviour can be stabilized is retained as a regression test. The thin commands that are clear operators and reuses are kept as scripts, specifying how they are entered, produced and used. The code and output used only for this inspection are cleared after the check has been completed; the user requests that the retained evidence be archived according to their actual purpose..
4. **Completion Conditions.** The regression test can be found and run separately according to the existing rules. The person who uses the tool can find the real access and the formal function is independent of the temporary file. `maintain-optional` with `maintain-tmp`.

<a id="tmp"></a>

## Create and clear one-time files or codes

1. See if existing pre-checks, results read or test answer the question. When a new one-time code is needed, the existing `tmp/<purpose>/` focus on scripts, temporary copies, outputs and logs. The pre-run confirmation tool does not disperse the generated file to another location.
2. A temporary script can call the official interface. The formal configuration, code, test, and document of the project should be separated from the temporary directory. This involves the temporary downloading or processing of a file system that requires the same data as the data, using the existing temporary storage under the data root.
3. When you have completed, check the actual use of this round of interim documents. The material that needs to be retained for a long period of time, or the material moved to the official location and validated for reading back by the corresponding category; the material that has a restoration purpose only retains the required part and the rest of the interim document is cleaned up.
4. **Completion Conditions.** The public entry point is not dependent on the provisional catalogue for this round, and the necessary evidence can be obtained from the official location. `maintain-tmp`.

<a id="environment"></a>

## Update the operating environment or depend

1. Check the actual Python, equipment and dependent versions from the project statement, the normal entrance, and the machine. The diagnosis of dependence first identifies the missing items with the current project interpreter. Updates the resource binding only when replacing the machine interpreter; the new package or version on which the user relies is declared by the existing project relying on the list.
2. Prioritizes the reuse of compatible environments. The parent area `envs/` or the registered location is to be arranged in an independent environment. The declared dependency is to be installed in the existing project mode or by `rh projects install`. The target interpreter, shared user and expected writing position are to be confirmed before running the installation.
3. When installed or switched, the affected import, equipment or normal entry is checked with the actual interpreter. Only the light inspection that confirms the condition when the condition of the equipment is involved is selected.
4. ** Conditions for completion. ** This machine binds, relies on statements and actually activates with the same interpreter, and the environment is in the agreed position, `doc/environment/` to indicate new requirements for preparation.

<a id="data"></a>

## Download, depress and prepare data

1. The data set, version, source, required file and directory shape are first identified from the loader and formulation, checking whether there are available copies of existing data roots. The same version is directly bound and read; the corresponding name position is used for additions.
2. Specifies the target and temporary location before you start download. The official data is placed in the working area `data/<dataset>/<version>/`, which is horizontal with ResearchHarness and the project. The item is read by configuration, parameter or binding. The current data root is followed when the atomic name is changed or the subsequent download is required. The common cache of the Hugging Face client is configured on the machine, and the prepared project input is positioned on the actual data root.
3. Retain the source version and apply the formulation to clean up the remaining balance of the current round.
4. The ** condition for completion. ** project can select the available version from the specified data root, and the data, download hold and pre-processing cache can account for the attribution.

<a id="assets"></a>

## Save resources and caches for long-term reuse

1. Make sure who reads the file, whether to cross-run the re-use, and how to rebuild it. Files that directly match raw data, such as depression and indexing, follow the working area data root; prepare the results, fixed questions and answers for the project to be used independently, or name the cache. `assets/` Resources; common caches reused by the client follows the configured location; indicators, projections and models generated by a given execution are running with the same time. `assets/`.
2. In the current group `assets/<type>/<resource>/`, the resources are placed at `files/`, and the dedicated script for this resource is placed at `scripts/`. Use a peer README to explain how users, sources, versions, updates and resources correspond to the selection conditions.
3. Validate the path, compatible version and format from the actual reader. The original resource retains its identity when it is still in use; it needs to be synchronized or read. The results of the one-time assessment follow the experiment and the user specifies the historical originals retained to be organized according to the historical resources of the project.
4. **Completion Conditions.** The user can find the correct version from the public entry point, knowing where the resource comes from and when it is updated. `maintain-optional`.

<a id="third-party"></a>

## Maintenance of third-party source codes and files

1. Check the project’s reliance declaration, upstream version and actual import. `third_party/<Upstream>/` corresponding object.
2. Keep the names, permits and sources in the upstream package and record the local differences. The appropriate code for the project is assigned to the actual responsible component or base layer.
3. Check the actual loaded version and the affected feature from the normal project entrance, update the source description and call the document.**Completion Conditions**The actual entry is still accessible. `maintain-optional`.

<a id="doc"></a>

## Update Document and Navigator

1. Find the existing page from README or `doc/README.md` to check the official command, default value, input conditions, results and actual path. If you have a page to answer, update the page; add a name page and index to the corresponding document position when you have an independent reader and theme.
2. When components, parameters, tasks, environments and experimental readings are changed, the actual responsible page is updated with the same batch of changes. Common examples refer to existing commands and small samples that can be reviewed. The historical trial report is described by the current configuration and evidence.
3. Check this affected relative link, path, illustrative command and the location of the result from the reader's portal by article. The example needs to be executed according to the type of operation and the authorization..**Completion Conditions**The reader is able to find the exact entry, operating condition, parameter meaning and result reading. `maintain-optional` and project manual.
