---
name: maintain-dataset
description: Add, modify or remove data sets, configuration presets and data options for scientific projects, and read and process actual dependency along sample preparation, registration and tasks.
---

# Data set maintenance

## Purpose

Allows the official mission to read the required sample through the physical data set in the root directory `datasets/` and to keep the source, label, division, preset and cache identity consistent. The whole project accepts and accepts at least one actual data set.

## Scope

Enter the target data set, the tasks used and the range of changes.

The actual commands, components and configurations are found from the `AGENTS.md`, README, or access instructions. First, a sample of the tasks is traced back to the call back to read, prepare and divide responsibilities.

- Add **. ** allows normal access to select a new data set, source or preset.
- ** Changes. ** changes the reading, preparation, division or sample interface of existing data sets, indicating which calls and historical results affect.
- Removes **. ** removes the specified preset, read-out, or task support. The range is the complete unmounting of the entire data set, confirming that the retention is still available. Original data, shared caches and historical results are processed as specified.

[Data Set Operating Scheme](references/procedures.md)Lists the document attributions, the sequence of implementation of the three types of changes and the conditions for their completion..

First determine the working area actually read by the task `data/` The decompression and indexing file of the directly supported data version follows the root of the data. `assets/` Resources. Locks and temporary storage follow actual writing positions, atoms write in the same file system. Hugging Face Original download and universal cache button `huggingface-maintain` processing of download instructions.

## Samples, labels, partitions or caches do not match configuration

Take a small batch of samples actually taken by the official mission and return the source, version, label, division and cache key for registration by sample status. Fix the preparation or logic of deviations. Rebuild the affected and renewable cache as agreed by the project and preserve the original input.

## Validation criteria

- Checks whether the sample identity, number, label meaning, sequence or shape, and whether the same data contract is followed in the case of a cache.
- If you are in a position to do so, you will be able to use the project’s comparative unit to verify the segregation, such as the object-level task of the study, by the identity of the object, and not just by line.

## Document Sync & Delivery

Synchronize data set entries, affected configurations and mission statements, and record how the source, sample, division or reading has changed. Deliver to humans the normal selection, actual sample evidence and impact on the comparability of existing tasks and experiments. `maintain-conf` Collaboration.

## Item-by-line

The data set is organized in terms of data sources and sample meanings. The named subset of the project definition is placed under the corresponding data set, indicating the selection, inclusion, labeling or division of differences and selection methods. The compatible preset for the same subset is written in the same entry. The text describes the source, sample unit, field and label, division and sample or preprocessing, selected tasks, output and limits. The different presets maintain the actual differences. The background is explained in the original paper or official description to determine the local behaviour by reading and formulating the project.

The text of the data set page presents the input, label, division and selection conditions, and a summary of how it supports the current selection is quoted in the data description. For example, indicate which queue the description of the supply classification applies.
