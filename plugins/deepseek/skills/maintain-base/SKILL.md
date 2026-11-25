---
name: maintain-base
description: Maintain the shared launchers and infrastructure of a research project. Use for command dispatch, cross-component wiring, resource selection, checkpoints, and shared result I/O.
---

# Maintenance of the research project base level

## Run the EverResearch CLI

Use Python 3.11, 3.12, or 3.13 to run `scripts/rh.py` from the current skill,
followed by the arguments after `rh`. For example, pass `projects project check <project-path>` to check a
project. Use `${CLAUDE_SKILL_DIR}` in Claude Code or Cowork and the staged skill
directory in Claude web.

The launcher uses the packaged runtime when available. GitHub marketplace
installs download the pinned wheel once and verify its checksum before use.
The launcher creates a private environment and may fetch Python dependencies.
With no Python execution available, review the files you can
access and tell the user which automated checks you could not run.

For a separate terminal installation, the official PyPI package is
`ever-research` from OpenSAE. The PyPI project named `researchharness` is
maintained separately.

## Purpose

The root directory `base/` is responsible for the open access, configuration synthesis, component selection, task distribution and common operation capacity. The original master package of the project is to be split according to actual duties, and the data sets, models and official tasks are to be assigned to the corresponding level I directory. The original public package is to be compatible with the map or thin access.

## Scope

The components' own semantics of data, model construction and scientific calculations are maintained. This range is determined by project README, configuration and physical call point.

From Item `AGENTS.md`,README Follow the command to the source of the configuration, base layer, component realization, task entry and result reader. `base/` Positioning and coordination of the public entry points and the coordination codes of existing projects moved to the directory under the same responsibility.

- Add **. ** connects to new project-level portals, modules or operational capabilities required by multiple callers.
- **Changes.** Adjustments to configuration resolution, distribution of components, running resource management or co-result reading and writing along actual calls to synchronize affected positions.
- **Remove.** Remove the specified distribution options, run support or result interface, first to process those who are still reading with its entry and historical results.

[Base level operating options](references/procedures.md)Description of who calls, under what conditions, and the order of implementation and conditions of completion when new, modified and removed.

## Check project maintenance before editing

Before applying EverResearch rules to project edits, check the project root for
`.researchharness/mode.toml`. If it is missing, follow the repository's own rules. When the user
asks to use EverResearch on that project, hand off to [maintain-project](../maintain-project/SKILL.md)
for authorized setup before applying these rules. Read-only inspection and planning can proceed
before setup.

If the mode file is present, run `rh projects project status <project-root>`. With `managed`, use
the reported guide and follow the authorized request. If the connection is unavailable or its
status cannot be verified, explain the gap and resolve it before applying EverResearch rules.


## Source code and path duties for the base layer

`base/` Indicates project-level responsibilities. `base/<Open Package Name>/` , in package `runtime/`,`api/` or a specific function name organizational code. Move the internal realization of a duplicate one-level job name to the actual responsible module, where the public import continues to be used through a packaged map or thin compatible portal.

The source root, configuration source, data and model binding, visible relative path and default root are determined item by item. The source runs the root from a verifiable project sign. The read-only command can use the package ' s configuration. The installation is based on a clear project workspace or output location. Validation of the package path or call directory to the declared workspace relationship to process the call for the missing writing position as publicly agreed. The compatible map of the aliases, input and historical results is maintained along the actual reading-take-end.

When this skill maintenance project is directly called, the base layer catalogue is drawn from the actual file and then the root path it uses is checked along the official writing entry. When a directory that repeats a level-I job name or the current directory that is not validated by the project logo is found, fix and rescale. Renaming or moving allows the running path resolution to rely on a stable project sign and open workspace parameter. Checks the map of the package name and the location of the file, as well as the actual documents to which the old public import refers.

## Cannot find configuration or error position at public entry point

By the same public command, the actual selected configuration, workspace and plan output are recorded from the project root and unrelated work directories, respectively. Read the path resolution or package resources that search for the first deviation, restore the achievement for which the target project is responsible and retain the old entry that is still in use. If there is no clear writing position, allow the entry point to identify the missing items before the official result is produced. Run the two work directories by way of the Python configuration preview or light-assembly integration of the project, and actually drop the disc by central layout and experiment checking. Report where the user is now starting, whether the original call is still available and the missing operational evidence.

## A large number of old module names conflict with path rules

First, you identify the old names from document commands, installation statements, normal import and real downstream. This lists the imports and orders that need to be retained, and moves the responsibilities within the project to a location that is consistent with the central rules. The public name is not the same as the physical path, maintaining the utensils through the project's packaging or compatible access. The entry that is still in use is verified in batches from the source code, editable installation and official installation, and then the central layout is cleaned. Freezing the upstream package is based on the source and version of its internal path, and the project's own-maintenance activity leads to the actual responsibilities.

## Validation criteria

- The normal startup is from the public command synthesis configuration, with the selected components, interpreter and path actually reaching the responsible module. Checks a default scene and a useful overlay or combination to follow the caller and result position.
- After a path adjustment, it is initiated from the root of the project, from the unrelated work catalogue and from the applicable stand-alone installation environment, using the same formal operation. Checks the selected root, the read configuration and the output path, as evidenced by the actual product or read-only preview. The visible relative path is analysed using the publicly available baseline and the current result is still readable from the public entry point.
- Independently installed writing tests cover two conditions. When the project's workspace or visible output is specified, the actual product is assigned to the agreed location; and when any irrelevant directory omits writing, you are ordered to give clear information before creating the product. The help, the formula list and the read-only configuration check verify that the resource in the package is readable.
- If you encounter unsupported combinations, lack of resources, or failure to run, check where the portal is stopped, whether the resources have been written down or loaded, and whether errors and existing products allow the caller to continue.

## Document Sync & Delivery

Synchronize the description of the base layer and the actual level I directory, which involves updating the parameter page in the order in which it enters into force, updating the environmental portal in the event of a change in operating conditions. Report how the user now starts, selects and reads the results, and how the existing calls and historical results continue to be used. `maintain-conf` Collaboration.

The changes are recorded in the project-by-project project file.

## Item-by-line

Write the parameters, selection of components, distribution and output by the public entry point. Multi-option sharing mechanisms focus on explaining the mechanisms, each with how the options change their operation, when they take effect, and what results they produce.

Readers at the base level should see where the configuration enters, how the components are selected and where the results are read on the current page.
