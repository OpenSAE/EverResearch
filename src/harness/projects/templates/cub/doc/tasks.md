# Tasks

## Purpose

Describe how classification, precheck and performance are selected for comparison, and what results are delivered for each.

## Scope

It is used to initiate work, to collate data and model combinations, to read indicators and products.

## Purposes and access

The normal entrance is `python -m cub_template` and the command is to be found [on the first page of the project](../README.md) (see current functionality and normal commands at the project entrance, e.g., for direct serviceable workstreams) and the [mission registration](../tasks/plugins.py)].

## Shared Parameters

The data sets, models, equipment and operational parameters are [parameter](conf.md) (for the configuration file, default values and overlay rules, the default values and effects of `training.batch_size` can be found). The results are listed from `inspect <run-directory>`.

## Component

### `classification`

- **function**. Train and evaluate the whole chart classification model.
- The **selection method**. The entry `run` is sent to this task by default.
- **Inputs and products**.Acceptance of registration 200 Category RGB Data sets and models, output training indicators, test indicators and final weights. Top-1 Proportion of samples with the same label for the highest score category.
- **Earmarked parameter**. `training.batch_size`, `training.epochs`, `training.learning_rate` Control and optimization of training workload.
- **Certification basis **. [Classification operation](../tasks/classification/operation.py) and [Runlink inspection](../tests/test_workflow.py)].

### `precheck`

- **Functions**.Examine the impact of the classification on the classification ' s workload by means of training and assessment steps, or by comparing the loading process.
- **Selection Method**.`precheck`,`benchmark` Sub-orders. Formal training also uses precheck.
- **Enter and produce**. Use a combination of classification support to train samples to generate precheckbacks or performance reports.
- The specific parameter **is**. `precheck.samples`, `benchmark.*` and `--candidate-workers` control range and objects for comparison.
- **Validation is based on**. [precheck portal](../tasks/precheck/task.py), [Performance comparison](../tasks/precheck/performance.py) and] [Outline precheck record](experiment.md) (for comparison results and limitations based on real operations, random initialization and fine-tuning of respective conditions).
