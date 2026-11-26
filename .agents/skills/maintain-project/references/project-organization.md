# Project access and structuring

## Purpose

The physical access and product identification functions, access to unfamiliar projects or the organization of parts of existing projects that need to be split, merged and reconnected.

## Scope

The scenes for which access, mobile code, merge duplicate functions or connect components have been identified. Select the steps for the actual changes.

## Positioning projects and existing access points

- When ** selects a directory. ** users request to mount a searchHarness source directory. New workspaces can place `ResearchHarness/`, share `data/` and each scientific project repository in the same parent directory. As necessary, a shared data directory is created. Only remote warehouses will have a copy of the work obtained in the parent directory.
- **Registration and transfer resources.** Use it. `rh projects --harness-root <ResearchHarness Contents> register <project ID> --path <project directory>` Mount. Follow-up will follow the same central path and will be performed if you need to synchronize your skills `apply <project ID>`,Use of registration resources when required `bind <project ID> --data <name>=<path>` or `bind <project ID> --python <Interpret path>`._Other Organiser ResearchHarness It's... `src/project/maintained/<project ID>/resources.json`,Replaces with an unlocked atom. The resource is given to the actual entry by the project-supported parameter or environment variable. The path within the warehouse is sorted by the root of the project or the clearly stated formulation position.
- Determines the repository to be read and the workspace to be changed, and looks at the project description, the current source version and the local changes. A copy of the work is obtained as authorized only when you have a remote address. A registered project follows the existing binding. ResearchHarness It's... `src/harness/core/README.md` Find the register of the project and the optional data catalogue and Python binding; when synchronizing skills is required, press `src/harness/projects/README.md` Use of existing access. The information is not yet fully available and the source-code mapping is still available in the working area.
- ** Keeps independent working methods. ** Reads from the project's own list of dependencies, commands, parameters and environmental variables to track installation, start-up, data and weight selection, and results. When new projects are created or organized, these links are left in the project's public entry point and document, so that users can use the project and the work area on which they need to rely.
- Searches for fixed system temporary paths, caches, and one-time scripts from the physical entrance. The project retains a list and separate installation steps. After access, Python can be bound and installed by ResearchHarness. Hugging Face downloads are managed by the client configuration of the machine, with its download instructions installed at `maintain-huggingface` and project-produced preprocessing inputs follow the named asset convention in `maintain-dataset`. One-time project works are done at `maintain-tmp` at project level `tmp/`, and functions already cited in the official process are moved to the responsible directory.
- When multiple items are verified by the same machine, the project interpreter is used to check the actual version, drive compatibility and import of the existing heavy reliance, and then to decide whether to reuse, isolate or install it separately. Stores the weights, input and construction of the downloads for a given evaluation in a location where they can be located. Record remote versions, drop points and validate values. When space is recovered, check the product and recurrence records and then clean up the large document that can be retrieved as authorized.
- When the public entry point calls the compiler's target, extension or external operator, the source code depends on the compiler, the target and the locking from the original build statement. Validation of the build and the minimum official call at the structural stage; real running records of the binary, build options and devices actually used. Optional interfaces, remote services and optional accelerations are enabled by selected workflows.
- First, find a command, workflow or Notebook for the actual use of the project. Prioritize the running examples in README, submitting scripts, configurations, and the source records of the recent results. If the entry is contradictory, distinguish between the current processes, historical processes, and examples along their actual calls and products; the unsupported entry is marked to be confirmed. Draws a structural sketch of the selected range, focusing on the entry and the main call using the `extract-structure` repository model.
- The whole project maintenance is to enter the applicable sections of the [project maintenance entry](../SKILL.md) to check responsibilities, call and deliver. The portal is used for access, whole project inspection and cross-component maintenance for unfamiliar projects, and is responsible for organizing specialized processing and overall acceptance. It needs to be checked the README in the CUB example directory printed by `rh guide example`, how configurations, components, pre-checks and results are linked from the operational class portal.

If the sketches need to be kept for subsequent reference, export a stand-alone HTML to be registered at the central `src/project/maintained/<project-id>/structure/` `rh projects --harness-root <ResearchHarnessdirectory> structure add <project-id> <HTMLpath> --revision <source-version-or-snapshot-id> --scope <analysis-scope>`.

## Establish source ownership

The named checkout is the project being maintained. Its own source stays project-owned even when
it comes directly from a public upstream repository. Start from its documented commands, installed
entry points, package declarations, and active tests. Identify the implementation groups that
serve those workflows and map each group to the layout by its real responsibility. Cover the
rest of the project-owned source, tests, configuration, and tools wherever their ownership can be
established. A representative workflow establishes the first migration and verification path.

Move existing implementations into their responsible areas, update their callers, and keep
working through the remaining groups. Preserve public names through packaging or compliant
launchers with help from `maintain-base`. Actual runtime paths must lead to the relocated code.
Thin adapters, demonstration workflows, and directory placeholders do not complete the migration
of the implementations they call.

Reserve `third_party/` for independently identifiable upstream components kept as dependencies.
Prefer incorporating their reusable parts where that is safe and meaningful. A minor upstream
component or a separately sourced component that relies on an inseparable upstream build,
generated interface, or update process may stay intact. Record its origin, callers, and why
retaining it is appropriate. Project-owned code that is difficult to move remains part of the
target. Finish independent groups and report the specific remaining implementation and blocker
when a required migration cannot be completed.

## Extract duties from mixed code

1. ** Tracks down from the entrance. ** Writes down the actual entry, feed parameters, default values, and overlay order. Following the import, function call, configuration identifier, or frame callback, you find the actual callable realization. The entry is Notebook, following the configuration, data, model, and result tracking between the units. When the workflow has multiple phases, you string up with the input and output of each command. When you see the external frame, the location items pass to its configuration, component, or return, and the output from the frame.
2. ** Look back from the results. ** Select the results of the real use of the process in the log, indicator, forecast or check point to find out who calculates, who wrote, who reads it. Pay particular attention to whether writing the path and configuration is determined by the boot script, environment variable, or frame. Find a file, function, configuration key, or Notebook unit to write down a specific missing item.
3. ** By work content. ** Answers four things to each function, class, code block or configuration that carries out the actual work: who calls it, what it receives, what it delivers, who continues to use it. At these four points, a document is located according to the work content when it does a few things at the same time. At the different entry points, a responsible position is maintained when the same call is made.

| Actual work seen in the original project | Attribution in the layout |
| --- | --- |
| Search for original inputs, sample reading, tectonic labels, division, sampling, sample transformation | Raw source files belong under workspace `data/`. Put reusable project-generated preprocessing inputs under `assets/prepared_data/<input-purpose>/files/`. Keep dataset reading and preparation code in `datasets/`. |
| Declaration of model variants, network construction, forward execution, load of model specific weights | The `models/` acceptor model achieves or adapts to a framework. The optimizer, rotational equivalent for the resumption of training follows the task or running process. |
| Select data and models, training, assessment, reasoning or analysis, calculation of loss and mission indicators | `tasks/` Accepts the tasking and research calculations. The task relies on the open interface of the component. |
| Default values, component options and overwhelm items | `conf/` Saves the project default configuration and options for access; the operational parameters for a single run are saved with the experiment. The meaning and inspection of models, data and mission-specific parameters remain the responsibility of the corresponding component. |
| Read command parameters, synthesize configuration, select data sets and models, distribute tasks, manage common operating resources | Open access, project-level coordination and shared capabilities are placed at `base/`. |
| Write or search for running logs, indicators, reports, projections and check points | The product belongs to the project ' s root directory `experiment/`. The general disk is run by the operating module, with the indicator meaning being assigned to the task. |
| Manual start-up, batch submission or demonstration | Keeps it in a script or Notebook if it has a stand-alone use, allowing it to call for formal realization. |

## Review and consolidate duplication of responsibilities

Five Level I directories `base/`,`datasets/`,`models/`,`tasks/`,`conf/` Data, models, and official tasks are performed in at least one actual case each; precheck has an independent function. The primary functions in the original master package and in the duplicate script are split according to this table, with the original command and evidence of behaviour being retained and then repeated at the same entry point. `rh projects project check --json` Validate disk structure and number of files.

### Categorized and merged by actual commonality

Check the questions, users, inputs, main steps, and results that are answered by the same level of the directory. First, you give a target structure named with actual responsibilities, indicating what each family shares, which sub-items are retained, and which have independent access.

| Contents | From what facts? | How do we classify and merge? |
| --- | --- | --- |
| `tasks/` | Training, complementary evaluation, analysis, reporting and methodological comparison for the same research purposes | The family retains a common input, distribution and indicator contract. |
| `datasets/` | Preparation or loading of the same source, sample identity, labelling protocol and data that can be shared | The queues, subsets and derivative panels of the same source data belong to the same group and share reading and preparation. |
| `models/` | Shared architecture, construction, input output and weighting agreements | You check the weight, input and output of different variants. |
| `scripts/` | Manual operations to be actually completed and formal capacity to be called upon | Common access and name options for the same operation. Restrict dependency and start-up, and separate processes or irreplaceable review tools retain their use. |

After moving to the same directory, check whether there are multiple currents of the same task step, similar data preparation or model structure, and are co-achieved by the call. Checks whether each of the new tiers locates the user with specific responsibilities and indicates why the directory that is still adjacent is maintained separately. Formal configurations are synchronized with the true owner ' s relative path, and the open choice is to agree to keep the record identity compatible with the project.

The review tracks the general catalogue-by-catalogue module of responsibility to the actual function. The training, analysis and evaluation of the same research objective is carried out by the task and sub-task, and cross-task data, models and implementation capabilities are placed under the corresponding responsibility.

When organizing a range involving multiple data sets, models, tasks or multiple operational links, before deciding how to split and move files, use `maintain-code` Reviews the actual call relationship. The skill determines whether it should be retained, merged, accessed or removed on the basis of the core use scenario. Read it through the skills portal of the current working area, using the migration and consolidation notes as needed. This section independently guides multi-component organization.

1. See ** for comparison duties along physical access. ** for callers, input, output, default values and side effects of the same link in each affected link. Prioritize data reading and preparation, model construction and weighting, task running and evaluation, and configuration, schedule and result reading and writing.
2. ** Finds what should be shared. ** The same function has multiple actual callers, and where the behaviour and agreement are consistent, priority is given to existing implementation. Differences can be expressed clearly in the configuration, sharing stabilization steps and retaining the default values for each entry. The scientific differences between data and labels, model structures and weights, mission goals and indicator calibres are clearly covered by the respective components.
3. **Implementation of consolidation in the organization.** Repetition of actual callers to achieve the same for fully based and duplicated responsibilities within this mandate, processing configurations, scripts, Notebook When you change scientific semantics, open results or resource inputs, you clearly influence and trade-off. There is insufficient evidence to select the place of compliance for a consolidated document, and the basis on which the record still needs to be checked..
4. ** Checks the affected normal scene. ** Checks the configuration, selection of components and agreement of results on which each entry is dependent against the call and product before and after the change. When approved, use the same input comparison along the representative entry involved in the merger to cover actual differences in components and old configurations or products.

## Map to sort files and entrances

- In the record of project maintenance, write down the "Present Location and User's Actual Responsibilities " , the results of the compliance review that has been implemented. The responsibilities are clearly achieved directly, and the mixed files are processed for the actual purpose. When the current functions are tied together, they will be placed in the standard position in which the function is performed and the open interface will continue to be split. Framework access and open interfaces will be carried by the achievement of compliance positions or thin matching. The historical originals and unquoted files will move according to the master table of the project's skills.
- When you move, split or merge, you update the import, configuration reference, command or script, relative path baseline and description. Route public commands and imports that depend on a prohibited path to `maintain-base` and collect evidence that their replacements work. Maintain the default and overwhelming order for organizing the parameters. `maintain-base`,`maintain-dataset`,`maintain-model`,`maintain-task` and `maintain-optional`.
- For example, `train.py` also randomly divides data, constructs models, trains and writes accuracy. First, you find the seeds and indexes used to divide, and assigns the corresponding logic to the data assembly; you load the model structure and weight to the model component; you keep the training cycle and the accuracy rate calculated in the mission; you pass the parameters through the entry, you save the indicators from the running module. The original command continues to be forwarded to the sorted task. If the project has only one end-to-end frame command, then you decide whether you need to dismantle the internal code.

## Connect to the project base level

Finds a synthetic configuration, selection or construction component, the actual code for the task from the normal command. `base/`.A physical link is available first. The entry request, the base layer positioning configuration, the data root and the results catalogue, access to data and models and call specific tasks, and the task calculation. Indicates where the project's default path and user input start, and how external resources go in. Recording results are read by the subsequent caller. The project needs to organize the entry according to the existing selection. `maintain-base`.

## Create Project Document

From README to the `doc/` index, map the actual one-level catalogue that is used. Sets, models, tasks, parameters, experimental fixed pages and knowledge, implement the environment, source structure portals, and register price equivalents that can be applied directly. Items using the project protocol can be reviewed from the above whole project to maintain entry specifications, updated in the format of the corresponding entry. Descriptions are from the actual command, effective configuration and readable products. Only observed operations or specific resistance attempts to enter the experimental report. Synchronize the entry and functional changes in the current setup to the corresponding page. The independent document is maintained with `maintain-optional`, the open parameters are changed by `maintain-conf`, and the structural entry interface `extract-structure`.

## Validation of components and experimental products

Inventory support from actual entry points and configurations before selecting verification cases.
Include every named dataset and model variant and each runnable task mode. Record supported
combinations and exclusions with the reason for each. Ask the owning skills to verify the real
components and fix recoverable problems within the authorized scope.

- [Dataset acceptance](../../maintain-dataset/references/procedures.md#accept-every-supported-dataset)
  obtains authentic sources and checks each applicable reader and split with representative samples.
- [Model acceptance](../../maintain-model/references/procedures.md#accept-every-supported-model-variant)
  verifies construction, real checkpoint loading or the declared scratch initialization, and a
  small forward pass for every supported variant.
- [Task precheck](../../maintain-task/references/procedures.md#run-a-bounded-precheck-for-every-task)
  tests the public task path through real I/O, effective data and model selection, bounded
  computation, and result readback. Reuse component evidence where its identity and execution
  environment match. Group selections that share the same relevant execution paths and contracts
  and state which entries each case covers. Test materially distinct branches separately.
- [Formal run choices](../../maintain-experiment/references/run-verification.md#prepare-the-formal-run-choices)
  give the user an executable option for each task, with the intended use, inputs, outputs,
  estimated runtime, and any remaining resource requirements.

Record each coverage item as passed, partially verified, or blocked with direct evidence.
Keep authentic data or weights pending when a fallback verifies only the contract. When code
moves, compare representative old and current outputs on the same inputs or state the missing
baseline. Read retained experiment outputs through the actual consumer. Full scientific
workloads remain available for the user's selection after technical acceptance.

## Item-by-line

Start with the formal registration, parameter entry and readable log count entries. Organize the body of the actual use. Place the famous subset, model variant and subtask at the corresponding superior, combine the synonym entry and the same decision, and write down the behaviour that the retention options will change. Available information can be indexed by entry.

The project document follows the project's actual catalogue and entry, following the project's usual name. The description used directly by a person is functionally and physically used, and each external description is linked to the summary required for the current reading.
