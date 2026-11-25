---
name: maintain-optional
description: Maintain standalone research scripts, tests, documentation, and reusable assets. Use for work such as plotting results, verifying a component, or updating a project guide.
---

# Maintenance of required assets for research projects

## Run bundled ResearchHarness commands

When a step calls for an `rh` command, run this skill's `scripts/rh.py` with Python
3.11 or 3.12 and pass the arguments after `rh`. For example, for a project check
run `python3 <absolute-skill-path>/scripts/rh.py projects project check <project-path>`.
Resolve the skill path from the current SKILL.md. On Claude Code and Cowork use
`${CLAUDE_SKILL_DIR}` for that directory, and on Claude web use the script staged in
the skill directory. Use an already available Python interpreter or let uv
select one if the host provides uv. The launcher uses the bundled OpenSAE wheel
and prepares a private Python environment automatically on first use. It may
fetch Python dependencies from the package index. Continue with file review if
the host cannot run Python or prepare the environment. State which automated
checks were unavailable. Never install the similarly named PyPI package.

## Purpose

Scripts provide operations that can be independently initiated, test the transformation of behaviour expectations into repertoire-executable inspections, document how the project is understood, used and maintained, and external documents allow the project to use traceable external results. The project document guides from a level-I catalogue to components, parameters, experiments, scientific knowledge, implementation of environmental and source code structures, and provides a means of use and factual basis for retroactive use.

## Scope

For adding, modifying or removing independent scripts, tests, documents, and external documents that are saved with the project. `AGENTS.md`,README,Available commands and users find real accesses. ResearchHarness Layout from the root of the item `scripts/`,`tests/`,`doc/` and `third_party/` Check-up. Existing items follow a price equivalent with a clear user.

- **Script.** Maintenance of batch, aggregate, export and demonstration portals with independent operators.
- **Test.** Formal pilot implementation compared to results `maintain-experiment`.
- **Document.** Navigates from README to the project document. Synchronize the first-level directory page with the reader's entrance, following the normal operations to verify links, examples and behavioral statements.
- **Long-term resources and external documents.** Reserves resources of long-term value at `assets/<asset-type>/<asset-name>/`. Each group uses `README.md` to identify sources, uses and updates to place the resource document and the dedicated processing scripts in `files/` and `scripts/` respectively. The common operational entry to the project is in the final directory `scripts/`. The official third-party source code is regulated by the source and licence of `third_party/`.

[Asset-to-needs operating programme](references/procedures.md)Read the corresponding section based on this asset type.

## Validation criteria

- When new, moved or restructured long-term resources, `rh projects layout check <project-root>` is called to check the location of resource groups and files, then read-in and produce along user or dedicated scripts. Synchronize the source, version and update method when changing external files with a recurrence value.

- Check each script group back from the project ' s normal entrance, installation statement, test import and document command. The script only saves manual operations with a clear user, data-processing, modelling and research tasks have been formally performed with manual scripts `datasets/`, `models/`, `tasks/`, respectively, and the same operation has been formally performed with a combination of parameters being carried over by a single entry. Name the entry, product, caller and resource requirements by purpose. Check the actual recovery value of the historical formulation; preserve the necessary formula and original evidence, and clean up copies that have been replaced and without users.
- Checks the normal parameters, the actual target module, the result path and the sum to be used for each change. First, confirm that the resolution of the option occurs before the large input, the creation of the result directory or the startup of the task is performed, before the help, plan or controlled replacement is performed. Use the controlled input to confirm the start parameters, the effective path and the output are readable, and the document example uses the same entry simultaneously.
- The document review follows two directions. First, the reader can find a complete description from the first-level directory, the current component and the independent command, and then the actual entry and evidence can be rechecked from the pages, links, examples and archives. The document directory retains a reading description and the necessary attachments; the source snapshot, the software environment, the running log, the test cache and the data are located or cleared by the actual user. The subject index is a complete list of the uses, status and scope of access, and the key page reviews the text for independent selection and interpretation by the practice scene.

- When you check `scripts/` as a whole, you can distinguish between a thin starter script, reusable realization, data preparation and one-time analysis from the current access point of the user command, scheduler and document location.
- When examining `tests/` as a whole, identify which assets will be automatically executed by calling from the discovery rules, CI commands and modules of the test framework. Distinguishing between behavioral regression, packaging, manual detection, export and outcome products.
- When adjusting the test layout or name, a certification authorization is given to use the routine test command collection model from the root of the project to record the findings and errors before, after and after the change. Checks whether the same name file conflicts under the actual import rules, whether the package can still be imported, and whether the example can still be found. The partial examples are collected separately through a full set of examples. There is a conflict and in this context, by naming the actual behaviour of the individual document, updating the direct reference and repeating the item-level collection.
- When you move the wrong file, check the project document, the official order, the startup record and the actual import. The old path is still open or has an existing caller. Only files that are used inside the original directory move with the caller. The receipt and inspection check separately the only attribution that has been achieved, whether the old entry is still useful, and how much has actually been reduced by the misplacement of the original directory.

- Each check starts with the actual user. Scripts check the public entry point, input output, side effects and result consumers; test whether or not to cover valuable actual behaviour and failure patterns; document check commands, default conditions, results and references from the reader's entrance; external file check sources, versions and actual callers.
- Keep official access, historical products from users and evidence of review, and identify old assets for which use is yet to be confirmed.

## Unable to use independent assets after relocation

Scripts modify the order of handling and actual implementation of parameters when large input is read at the aid or planning stage. When reorganizing and unable to collect, test the actual collection command location file, clamp or import from the test frame, recollect and run the approved affected cases once the document is repaired. When the document example fails, check the current public entry point and call directory, restore the command and result link. When processing the third-party source code, identify the upstream source and version, retain the inner path and file name of the package on which the downstream depends, and adapt the project to the actual utilisation module. Validate representative behaviour from the existing entry point, the path attribution and file name using a central layout check.

## Document Sync & Delivery

The entire project document maintenance must be completed with `doc/environment/README.md` and a link from `doc/README.md`. Check the interpreter, rely on installation, equipment and data preparation, and light authentication commands along the public entry point.

Synchronizes the description of the first-level catalogue of assets and the index to the project document, with new entry points or updates of the user-readable pages when you rely on them. Report the asset now supports who does what, the basis for the inspection, and the public entry point or downstream impact.

When you review the project document in its entirety, complete the applicable fixed page and index links from the physical first-level directory and the open entry against the project project document specifications. When you encounter another machine or an old-signed absolute path, check the current registration and actual input, then give the machine the command that it can execute or specify its replacement parameters and the conditions for preparation. After the path has been migrated, run an executed offline example or a read-only preview from the directory specified in the document. The history report continues to explain the original record by source.

The changes are recorded in the project-by-project project file.

## Item-by-line

The actual use is identified from registration, configuration, public orders and readable experimental records. New, rewrite, merge, split or delete entries, as required, are explained by the parent's description of the common content, and the actual difference is explained by a sub-item. The text is explained on a page-by-page basis, which allows for an understanding of functions, conditions of use and results; links are used to verify and read in-depth. The known facts give priority to the project basis, to which the general knowledge and data set or model can be supplemented by available papers, author information and official documents.

When the maintainer reads the document, it follows the natural terminology available to the project from the description of the true directory and the responsibilities of the document. Each reference to another document contains a key summary, including the purpose, scope of application, main elements and a practical reading example. Key usages and results are written on the current page.
