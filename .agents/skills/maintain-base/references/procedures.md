# Base level operating options

## Purpose

Project-level coordination logic from formal commands to components, tasks and results is located and maintained through the order in which documents are attributed and called.

## Scope

Adds, modifies or removes the base layer function of a scientific project. The table position is used relative to the target project root directory. `src/` Layout Main Package From `src/<Main Package>/` Find. Existing items are based on the actual price equivalents called at the normal entry. `base/` , the required modules are created on a functional basis.

## Attribution of files

| Location | When to use | Responsible for content and call relationships |
| --- | --- | --- |
| Root directory has command scripts, `<main-package>/cli.py` or `<main-package>/__main__.py` | When the researcher starts or reads the results from the command line | Receives commands and parameters, calls the base layer or the official reading entrance, returns exit status or displays information. |
| `base/runner.py` or main package already has a running entrance | When a process requires a combination of configurations, data sets, models and tasks | The component option is obtained from the configuration resolution, and a data reader or model is created using the public interface of the component, and the task is called. The resource that needs to be released after failure is managed by the operational code that obtained the resource. |
| `base/config.py`, `conf/config.yaml` and the configuration or formulation actually used by the project | When multiple formulations, environments or covers need to be synthesized | The primary configuration provides defaults, `conf/dataset/`, `conf/model/`, `conf/task/`, etc. already available groups provide options that can be selected independently. The base layer synthesizes the parameters in the current order of the project and gives them to the caller. The single-acting configuration is saved with the running record. |
| `base/paths.py` or a path module already exists for the item | Default configuration, data and result path needs to be aligned across the portal | The project description indicates the starting point for the relative path of the command line. |
| `base/registry.py` or `<main-package>/registry.py`, and `datasets/plugins.py`, `models/plugins.py`, `tasks/plugins.py` or their equivalent | When data, models or tasks need to be independently selected with a configuration identifier | Declaration of identification and public realization on the side of the component. The project registration entry is responsible for decomposition, which is used by the operator. A small fixed set can be called directly by the operator. |
| `base/runtime.py` or existing equipment, environment module | When normal access requires the management of equipment, precision, seeds, process groups or other running resources | The mission uses the operating environment to carry out its own calculations. |
| `base/checkpoints.py`, `base/records.py` or already available result modules | When multiple entry points use the same inspection point format, or tasks need to be recorded in a uniform state of operation and product | Common reading and writing code processing paths, files and status records. Models explain weights, tasks decide to save time and business fields, and the result is that the reader finds the product using the registered record interface. The corresponding module is activated on the actual call. |
| `datasets/`、`models/`、`tasks/` | When the location component is handed over and the behaviour of the exclusive is modified | The data set is responsible for the sample, division and metadata. The model is responsible for the construction, forward and weighting syntax. |
| `experiment/` corresponding to running directories, README and `doc/` | When the result is found or the official use is updated | The operational record indicates the configuration and location of the product in effect. README gives the command and entry. The affected component describes the parameters, results and restoration conditions. |

## Increase

1. From a given situation of use, write down the "command or interface effective configuration data and model entry Query mission entry Quest reader". For each transfer, find the incoming object, parameter or file, and the location responsible for releasing the resource or recording the status.
2. Reload the existing configuration and component portal first. The public option requires to update the corresponding registration, public configuration and operator when the identification selection is made. The fixed access is directly connected. Common equipment, process group or result reading and writing is done by document attribution and the actual caller is received.
3. Follow the new logic from the README command or the official caller to confirm that the entry can enter the expected parameters, that the mission can obtain the desired object, and that the subsequent reader can locate the product. A minimum running check is authorized. The document indicates the actual entry and the requirements.

## Modify

1. Finds the commands, public identification, formulation, call order and product reader affected. Checks the defaults and overwhelming order when adjusting the configuration. Checks initialization, execution and exit when adjusting running resources. Checks the file path, fields, old formats and restores the required state when adjusting for reading and writing.
2. Put the change in the actual responsible file. Configure value `conf/` Platforms, equipment and other common processes are maintained at the base level. Synchronize the configuration, caller and description involved.
3. Check the public entry points affected and the old results that still need to be read. When it comes to the management of resources or parts of the product after failure, describe the current behaviour and the affected reader.

## Remove

1. Finds the entry, registration, default, configuration, direct call, and historical result readers of the ability to be removed. First, you implement an alternative path for the retention process, or you identify the affected call and result.
2. Removes the exclusive access, realizes, configures and explains within the limits of approval, and retains the common functions and historical reading portals that are still required for the remaining process. Checks with the retention portals to interpret their options and find the effective configuration and product in the current way.

## Points for reference items

The `train.py` and `sample.py` call `base/runner.py`. `base/config.py` Loads `conf/`, `base/runtime.py` the team of preparation equipment, accuracy and training processes, `base/checkpoints.py` provides the checkpoint reading and writing. The training mission contains optimizers and determines what status to keep. The CUB template using the master package running directory is coordinated by `cub_template/runtime/runner.py` and the root directory `base/runner.py` corresponds to the same function.
