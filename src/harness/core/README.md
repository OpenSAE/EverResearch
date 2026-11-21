# Public function in central workspaces

## Purpose

The location of the work area required for the registration of the project path, the catalogue of research projects and the examination of experimental products, as well as the atomic preservation of the in-house information and the recording of the product.

## Scope

It is used to locate the machine project, the receiving and inspection layout, the preservation of resource binding and structural results, and the recording of documents generated in the central workspace by independent tools.

`central.py` locates the source path of the registered item. `workspace.py` provides an atomic file for writing and workspace product logs. The shared skills, resource binding and structured results command is provided by `src/harness/projects/` and the document processing and environmental tool by `src/harness/utils/`.

`project.py` passed `rh projects project check <project root directory>` Checks five entity-level directories, readable configuration portals, foundation level realization, at least one actual data set and model and non-precheck missions, and check prechecks for pre-realization and embedded component trees in the base level. `base/`,`tasks/`,`scripts/`,`tests/` And recognizable old source root layers. 15 Upper limit for a direct file. Root level `datasets/` and `models/` Subtree exemption check. JSON It's... `components` List components found on disk; actual business behaviour is validated by the official project entry.

When there are more than 15 direct subdirectories, `project check` reports the path, number of files and number of subdirectories by `directory_reviews` for functional inspection and repair. The independent functions in the existing directory are based on actual calls. The number of documents remains at the mandatory limit of 15.

`layout.py` Checks the project tree in accordance with the central rules. `rh projects layout check <project-root>`. `checked` records the total number of items scanned, `violations` lists the locations, rules and expected structure. The command exit status `0` indicates the pass, `1` indicates the violation or failure of the check, and can serve as a layout check order in maintenance and continuous integration.

`experiment.py` Use the `rh projects experiment check <project-root>` independent review of the experimental list, effective configuration, operational identity and documentation of the official product. `runs` in JSON records the number of actions scanned. Completed operations need to be read back from the public entry point of the project, confirming the actual results and their use.

`precheck.py` passed `rh projects precheck check <project root directory> <Directory of successful execution> <Synchronising "%s"> --max-seconds <seconds> --max-samples <Number>` Check the precheck evidence generated at the normal entrance. `precheck_seconds` and precheck reports, in reports `samples_checked` Record the number of actual samples processed (received separately for multiple treatments of the same sample) and record them prior to the start of formal computations `formal_started`.Record when precheck failed `automatic_precheck` Commands to repeat the experimental path and product rules, and to read the existing records.

`project check` Check it out. `doc/environment/README.md` the text and `doc/README.md` The environmental conditions and the accuracy of the light orders are reviewed along the project entrance.

[Project access and in-house resources](PROJECT.md)Description of project source code, data, Python and how the results of the structure are positioned and applied to the registration of projects and the management of local resources.
