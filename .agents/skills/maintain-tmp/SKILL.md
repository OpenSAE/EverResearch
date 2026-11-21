---
name: maintain-tmp
description: One-time scripts and temporary documents to organize and close a scientific project. tmp Work directories, clearing of temporary content or access to official directories for continuous use.
---

# Temporary work on projects

## Purpose

Provide a centralized location for a one-time check, a trial script and a temporary intermediate document so that the public entry point, document and configuration can always be used independently.

## Scope

The skills' own work materials are kept in accordance with the skills catalogue.

## Central path check and project restoration

ResearchHarness unified the maintenance of document paths, directory and naming. The assistant performing the research project uses read-only ResearchHarness and its verification portals to restore the public entry point, logic and results of the target project within the permitted range. When it is considered that the error or the rule is too strict, the inspection order, rules, path, reversible evidence and impact are included in the human-oriented report and continue to be independently completed.

## Select Temporary Directory

1. See if the existing commands, `tasks/`, `scripts/`, `tests/` and `conf/` can be completed by calling the public entry point or modifying it as required. Only if the work is one-time and the existing entrance and official location cannot be reasonably connected will the temporary code be placed at `tmp/`.
2. Each time a separate directory is created under the root item `tmp/`, named after two to three specified words, e.g. `tmp/check_batch_shape/`. A temporary script, a copy of input, an output and a log from the same processing is placed in the directory.
3. It is forbidden to import, call, configure, link, describe or rely on `tmp/` documents in other level I directories of the project. The official code, command, document and continuous integration only uses the public entry point and result of the project. Temporary scripts can call the official interface.

## After-run processing

- When long-term use is required, the actual use will be judged by `maintain-code` along the normal entrance. The regression check will enter `tests/`, the independent manual entry will enter `scripts/`, the scientific calculation will enter `tasks/`, and the public configuration will enter `conf/` or the corresponding official module.
- This created temporary directory is deleted when the work is completed and the contents need not be retained.

## The temporary catalogue became a dependency on the public entry point.

Check for references to this temporary position in official commands, imports, configurations, and documents before cleaning up. When a real user is found, the long-term achievement and necessary input are returned to the official responsible position, and the synchronised call is made. Use the Python portal to confirm in a quarantine copy that the temporary directory is still functioning normally when it is not available, and call the central layout to check for official attribution.

## Documents processed by actual attribution

- **Environment.** Project Custody Reliance List. `src/project/<project-id>/resources.json` for ResearchHarness saves Python binding. `rh projects install` Use bound Python to create this work directory under the center `.workspace/harness/projects/install/` to be recovered upon exit.
- **Structural results.** Structure pages, sources and review records registered with ResearchHarness are kept at `src/project/<project-id>/structure/` for subsequent access by source version and analysis.
- **Data and models.** Human Face downloads to `huggingface-maintain` to manage download locations and caches. Formal data and their pre-processing, reusable caches and data locks are the corresponding dataset directories under the selected data root. The pre-processing of the atom landing disk is required to remain in the file system where the data is located, e.g. `data/<dataset>/tmp/`.
- **Experiments and evidence.** Rereviewable validity configurations, logs and indicators are run in the corresponding experiment. The document to be read in the step or session is stored directly at the appropriate official location.
- The **internal temporary file.** tools are created anonymously, and short life-cycle files that are consumed and automatically recovered within the same process are processed by the tool.
