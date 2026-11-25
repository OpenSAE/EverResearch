---
name: maintain-tmp
description: Organize or clean up one-off research work. Use for disposable scripts, scratch files, and temporary documents, including deciding where reusable work should live.
---

# Temporary work on projects

## Purpose

Provide a centralized location for a one-time check, a trial script and a temporary intermediate document so that the public entry point, document and configuration can always be used independently.

## Scope

The skills' own work materials are kept in accordance with the skills catalogue.

## Check project maintenance before editing

Before applying EverResearch rules to project edits, check the project root for
`.researchharness/mode.toml`. If it is missing, follow the repository's own rules. When the user
asks to use EverResearch on that project, hand off to [maintain-project](../maintain-project/SKILL.md)
for authorized setup before applying these rules. Read-only inspection and planning can proceed
before setup.

If the mode file is present, run `rh projects project status <project-root>`. With `managed`, use
the reported guide and follow the authorized request. If the connection is unavailable or its
status cannot be verified, explain the gap and resolve it before applying EverResearch rules.


## Central path check and project restoration

EverResearch unified the maintenance of document path, directory attribution and naming. The assistant performing the scientific research project uses read-only EverResearch and its verification portals to restore the public entry point, logic and results of the target project to the extent permitted. When error is considered or the rules are too strict, the inspection orders, rules, pathways, reversible evidence and effects are included in the human-oriented report and the independently completed project is maintained.

## Select Temporary Directory

1. See if the existing commands, `tasks/`, `scripts/`, `tests/` and `conf/` can be completed by calling the public entry point or modifying it as required by duty. Only if the work is a one-time job and the existing entrance and official location cannot be reasonably connected will the temporary code be placed at `tmp/`.
2. Each time a separate directory is created under the root item `tmp/`, named after two to three specified words, e.g. `tmp/check_batch_shape/`. A temporary script, a copy of input, an output and a log from the same processing is placed in the directory.
3. The import, call, configure, link, describe or rely on `tmp/` for other level I directories of the project is forbidden. The official code, command, document and continuous integration only uses the public entry point and result of the project. Temporary scripts can call the official interface.

## After-run processing

- When long-term use is required, the actual use will be judged by `maintain-code` along the normal entrance. The regression check will enter `tests/`, the independent manual entry will enter `scripts/`, the scientific calculation will enter `tasks/`, and the public configuration will enter `conf/` or the corresponding official module.
- This created temporary directory is deleted when the work is completed and the contents need not be retained.

## The temporary catalogue became a dependency on the public entry point.

Check for references to this temporary position in official commands, imports, configurations, and documents before cleaning up. When a real user is found, the long-term achievement and necessary input are returned to the official responsible position, and the synchronised call is made. Use the Python portal to confirm in a quarantine copy that the temporary directory is still functioning normally when it is not available, and call the central layout to check for official attribution.

When formal results have been read from or published using the temporary directory, trace both the readers and the commands that rebuild or replace reports, archives, or other published outputs. Before cleanup, hide the temporary path in an isolated project copy and verify the relevant public read and republication commands within authorization. Use the manifest or output contract to check that the new publication retains the complete expected set of files. A matching backup establishes what is available to read. The republication check establishes whether a later invocation can rebuild the expected output safely.

## Documents processed by actual attribution

- ** Environment. ** Project Custody Reliance List. `src/project/maintained/<project-id>/resources.json` for EverResearch saves Python binding. `rh projects install` Use bound Python to create this work directory under the center `.workspace/harness/projects/install/` to be recovered upon exit.
- ** Structural results. ** Structure pages, sources and review records registered with EverResearch are kept at `src/project/maintained/<project-id>/structure/` for subsequent access by source version and analysis.
- ** Data and models. ** Human Face downloads to `maintain-huggingface` to manage download locations and caches. Keep official input data under workspace `data/`. Store reusable project-generated preprocessing inputs as named assets following `maintain-dataset`. Place locks beside the resource they protect. Stage atomic replacements on the destination filesystem, using a temporary location near the data or asset being replaced.
- ** Experiments and evidence. ** Rereviewable validity configurations, logs and indicators are run in the corresponding experiment. The document to be read in the step or session is stored directly at the appropriate official location.
- The ** internal temporary file. ** tools are created anonymously, and short life-cycle files that are consumed and automatically recovered within the same process are processed by the tool.
