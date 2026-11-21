# Central work area, in-house resources and project inspection

## Purpose

The location of the work area required for the registration of the project path, the catalogue of research projects and the examination of experimental products, as well as the atomic preservation of the in-house information and the recording of the product.

## Scope

It is used to locate the machine project, the receiving and inspection layout, the preservation of resource binding and structural results, and the recording of documents generated in the central workspace by independent tools.

## Workspaces, registration and resource binding

### Workspace Level I Directory

```text
workspace/
├── ResearchHarness/
├── data/
├── SAEBase/
└── <Other scientific projects>/
```

`workspace/` is the parent directory selected for this machine. The project warehouse, ResearchHarness and share `data/` laterals. Data can be organized by name and version at `data/<dataset>/<version>/`. When there is a shared weight or environment, additional `weights/`, `envs/`. The project's internal `conf/`, `experiment/` and dedicated data remain under project management. `src/project/maintained/<project>/` for ResearchHarness saves the project's resource binding and structural results, `.workspace/` saves the central running status and process file.

Select a source directory with `rh projects --harness-root <ResearchHarnessdirectory>`, using its parent directory as a workspace. You can check from the source code or editable installation to the current command. The shared data directory is created and bound as required by the item.

The relative path entered in the project registration starts with the command execution directory. When you bind the data and Python, the relative path entered starts with the root of the project. When the project is located in the same workspace, the records use the workspace relative to the workspace, and the skills-sharing link to the workspace project also uses the workspace. The external directory continues to use the absolute path of the machine. The old absolute binding continues to be read. Before moving, you can re-register the project at the original location, bind the associated resources and apply the shared skills. The Python environment itself follows the conditions for its installation and relocation.

| Information | Purpose |
| --- | --- |
| `.workspace/harness/core/central/project_roots.json` | This machine map of the project identification to the source directory. Written by `rh projects register`, the registered item follows directly. |
| `src/project/maintained/<project>/project.yaml` | The central identity of the known project and the optional shared skills settings. Enables the project when it is newly registered, and syncs the project link when it is applied. |
| `src/project/maintained/<project>/README.md` | The project entrance and first-line feedback are maintained on a project-by-project basis. |
| `src/project/maintained/<project>/resources.json` | This machine has a directory of named data and selected Python. Ties the entire file to the atom. |
| `src/project/maintained/<project>/structure/<artifact-id>/` | `index.html` Save Structure Page, `artifact.json` Save Source and Version, `decision.json` Save Comments After Review. |

The project's own code, scientific configuration, operating environment requirements and experimental results belong to the project. The central data and the Python path are selected by the machine and are processed by the project's original entry after start-up. Existing projects can obtain a directory of names using command parameters or environmental variables.

If the old `src/project/<project>/` is still used, the command will follow the old record when the new directory has not been created. Move the entire project log directory to `src/project/maintained/`, and keep the project identifier, resource allocation, structure page and review log. This machine log directory is ignored by Git.

### Installation projects depend on

Reliance on the List and Python and equipment requirements. Select to use the configured mirror environment, or the parent area `envs/` Prepare project environment and re-register it Python.The following orders are executed from the father's work area:.

```bash
rh projects --harness-root ./ResearchHarness bind example --python ../envs/example/bin/python
rh projects --harness-root ./ResearchHarness install example --requirements requirements.txt
```

The relative path of `--requirements` starts with the root of the project. The installation and project start with the same binding. When you need to retain the CUDA version of PyTorch with a mirror, the installed command plus `--preserve-package torch` is used as a constraint in the resolution of dependence. A stand-alone work directory is created every time it is installed in ResearchHarness `.workspace/harness/projects/install/` and is recovered when it is withdrawn. If the project shares the same interpreter, the effect of relying on change on the shared project is confirmed before installation.

## Central realization and inspection reports

`central.py` locates the source path of the registered item. `workspace.py` provides an atomic file for writing and workspace product logs. The shared skills, resource binding and structured results command is provided by `src/harness/projects/` and the document processing and environmental tool by `src/harness/utils/`.

`project.py` passed `rh projects project check <project root directory>` Checks five entity-level directories, readable configuration portals, foundation level realization, at least one actual data set and model and non-precheck missions, and check prechecks for pre-realization and embedded component trees in the base level. `base/`,`tasks/`,`scripts/`,`tests/` And recognizable old source root layers. 15 Upper limit for a direct file. Root level `datasets/` and `models/` Subtree exemption check. JSON It's... `components` List components found on disk; actual business behaviour is validated by the official project entry.

When there are more than 15 direct subdirectories, `project check` reports the path, number of files and number of subdirectories by `directory_reviews` for functional inspection and repair. The independent functions in the existing directory are based on actual calls. The number of documents remains at the mandatory limit of 15.

`layout.py` Checks the project tree in accordance with the central rules. `rh projects layout check <project-root>`. `checked` records the total number of items scanned, `violations` lists the location, rules and expected structure. The command exit status `0` indicates the pass, `1` indicates the violation or failure of the check, and can serve as a layout check order in maintenance and continuous integration.

`experiment.py` Use the `rh projects experiment check <project-root>` independent review of the experimental list, effective configuration, operational identity and documentation corresponding to the official product. `runs` in JSON records the number of operations scanned. Completed operations need to be read back from the public entry point to confirm the actual results and their use.

`precheck.py` passed `rh projects precheck check <project root directory> <Directory of successful execution> <Synchronising "%s"> --max-seconds <seconds> --max-samples <Number>` Check the precheck evidence generated at the normal entrance. `precheck_seconds` and precheck reports, in reports `samples_checked` Record the number of actual samples processed (received separately for multiple treatments of the same sample) and record them prior to the start of formal computations `formal_started`.Record when precheck failed `automatic_precheck` Commands to repeat the experimental path and product rules, and to read the existing records.

`project check` Check it out. `doc/environment/README.md` the text and `doc/README.md` The environmental conditions and the accuracy of the light orders are reviewed along the project entrance.

Project access commands and shared skills are available in [scientific project access and maintenance](../projects/README.md#project-setup) for synchronized skills, start-up of selected projects and viewing of structural results.
