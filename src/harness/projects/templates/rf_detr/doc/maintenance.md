# RF-DETR layout migration

## Purpose and main function

Map the former physical layout to the installed detector, dataset, training and export APIs.

## Scope of application

Use when validating detector commands, model and dataset selection, training or export.

## Component maintenance

| Responsibility | Entry and evidence | Change or retained contract |
| --- | --- | --- |
| Shared runtime | `python -m rfdetr fit --config rfdetr_nano --print_config` and a wheel built from the source distribution | Setuptools maps physical source directories to the installed `rfdetr` package. Runtime helpers and public entry points resolve through editable and wheel installs. |
| Datasets | `rfdetr.datasets.build_dataset`, the COCO subset manifests and WebDataset CLI tests | Reader dispatch and dataset transformations live in `datasets/detection_data/`. The official COCO annotations, image identities and split metadata stay with the original input and run records. |
| Models | `rfdetr.models`, `RFDETR.from_checkpoint` and `models/detection_transformers/backbone/dino_architectures.py` | Model code and DINOv2 architecture definitions live in `models/detection_transformers/`. The saved Nano and Medium checkpoints reload on CPU as the expected classes with resolutions 384 and 576 and 90 category slots. |
| Tasks | `rfdetr fit`, `rfdetr validate`, `rfdetr test`, `rfdetr predict` and their Lightning regressions | Training code and shared metrics live in `tasks/train/` and `tasks/evaluation/`. The named launcher uses the same fit command. A generated-shapes CPU run completed one training and one validation batch, then the results command read its completed manifest. Direct calls accept a caller-selected output directory. |
| Parameters | `conf/config.yaml`, the Lightning parser and the tests for saved overrides | The eleven YAML examples became named sections with identical parsed values. The CLI accepts historical recipe paths and existing user-supplied configuration files. |
| Experiments | `scripts/train_experiment.py results`, the three stored execution manifests and validation CSVs | COCO subset results move to `experiment/coco2017_subset/<model>/train/pretrained_finetuning/`. The reader resolves the original addresses and returns current artifact locations. The original configs, execution records, data IDs, trained weights and metrics were retained. |
| Scripts, tests and docs | MkDocs, pytest collection, workflow shell tests and the code that produces or consumes each path | Build scripts use `scripts/documentation/`; notebooks live in `scripts/examples/cookbooks/`; published routes and notebook download addresses are mapped to these sources. Product, integration and fixture directories replace the old test paths. Root agent instructions are located in `.claude/CLAUDE.md` for Claude Code, with the common rules in `AGENTS.md`. |

## Direct files in active directories

The mapping groups roles while retaining separately maintained behavior. In `models/detection_transformers/`, backbones, heads and deformable attention are distinct groups. The remaining files own detector assembly, matching, loss, positional encoding, weights and postprocessing. `datasets/detection_data/` has shared contract and transformation modules plus separate COCO, Objects365, YOLO and streaming readers whose formats and split rules differ. `tasks/train/` keeps Lightning modules, trainer construction, optimizer and checkpoint internals together, with callbacks grouped below it. `base/utilities/` contains cross-component primitives for distributed execution, files, logging, tensor handling and optional imports. In `base/detector/interfaces/export/`, common export interfaces and dispatch share a directory, with format-specific code below it.

The largest test branches are datasets, export, inference, prediction, models, training and utilities. Their direct modules exercise distinct formats, entry points or contracts. Shared fixtures and probes have a separate directory, and format, backbone, head and callback tests have local subgroups. The documentation reference and export branches keep separate pages for each exposed model, config class and deployment backend so individual website URLs remain available.

## Verification during the original migration

The initial layout scan exited with status 1 and reported 35 paths before recursion could enter several rejected directories. The completed scan exits with status 0. The migrated suite collects 12,020 tests. The targeted configuration, CLI, model, export, documentation workflow and metrics suite ran 555 passing tests with 13 skips. The historical COCO run results read back at their original and current addresses, and the saved checkpoint objects load through the public API. MkDocs uses the installed package for the API reference.

The recorded COCO measurements describe the small existing acceptance subset. No new COCO training or full-dataset benchmarking was needed for this source and result migration.

## Follow-up maintenance and verification

| Responsibility | Current entry and evidence |
| --- | --- |
| Shared runtime | Setuptools maps `base/detector/`, `datasets/detection_data/`, `models/detection_transformers/` and the task directories into the public `rfdetr` package. Public package and backend imports work from the editable checkout. The MkDocs build uses a freshly built wheel. |
| Datasets | The named launcher selected the COCO reader and built the training and validation splits of the existing local subset. A missing COCO directory failed in the same reader during automatic precheck. |
| Models | The bounded training check used the Nano recipe and an existing Nano checkpoint. The public checkpoint reader restored the retained Nano and Medium models at 384 and 576 pixels. |
| Tasks | `scripts/train_experiment.py fit` delegates its automatic precheck to `tasks/precheck/` and proceeds to the existing Lightning fit on success. The precheck records actual samples and original errors. The direct Lightning CLI and Python APIs use their existing task setup. |
| Parameters | The checkout still resolves named and old-path recipes through `base/detector/runtime/recipes.py` and accepts explicit overrides. The launcher saves the effective configuration for each current run. |
| Experiments | The official results command opens the three retained COCO records using their current or historical addresses. The records now reference canonical manifests and effective configurations, with the original execution JSON retained. TensorBoard events moved to per-run logs. Historical reports are stored in the [COCO verification archives](../assets/history_experiment/coco_training/README.md). |
| Scripts, tests and docs | The [environment page](environment/README.md) covers setup and bounded checks. The documentation source uses `doc/code/website/source/`; MkDocs retains the published routes. Tests are organized by behavior and their checkout workflow references were updated. Pytest collected 12,065 cases and the latest targeted regression selected 84 passing cases. |

The follow-up structural check inspected 809 paths and reported 31 naming violations. The affected paths include the checkout name, existing Python module names, the MkDocs configuration and retained experiment identifiers. The independent experiment check passed for all five retained executions.

The bounded verification used an existing Nano checkpoint and the local COCO subset, with two images per batch on the CPU. The automatic precheck processed four images in 83.09 seconds from launcher entry. The launcher then completed one training and one validation batch. Its result command read the metrics and listed the saved checkpoints. The same launcher rejected a missing dataset with a specific COCO path error and recorded that formal training had not started. The central precheck command accepted both executions with a 120-second limit and a four-image limit.

The first rehearsal's configuration, command, metrics and checkpoint digests are in the [rehearsal archive](../assets/history_experiment/coco_training/files/startup_verification.tar.gz). Removing its four duplicate checkpoints reclaimed 854,780,596 bytes. The full later verification and all three original COCO training executions remain available under `experiment/`.

## Current checkout verification

Use a dedicated interpreter and bind your own dataset and model weights in the copied template.

| Responsibility | Current evidence |
| --- | --- |
| Shared runtime | The checkout interpreter imports the public package through the existing editable mapping. The module entry accepts a named segmentation recipe from an external working directory. The source distribution and wheel both build with the public package layout. |
| Datasets | The bounded CPU checks used `datasets/detection_data/coco.py` through `tasks/train/module_data.py`. The archived protocol identifies 16 training images and eight validation images with disjoint official COCO IDs. The four command-line tasks rejected a missing dataset at precheck, before creating the requested formal output. |
| Models | `RFDETR.from_checkpoint` restored the archived Nano and Medium detectors on CPU at 384 and 576 pixels with 90 COCO category slots. Nano returned detections from one image and validation metrics from the eight local validation images via the public Python API. The active model implementation is in `models/detection_transformers/`. |
| Tasks | `tasks/train/command_line.py` passes the parsed fit, validate, test or predict command to `tasks/precheck/` before constructing the formal run. CPU fit checked two images and then wrote metrics and checkpoints. Validate, test and predict each checked one image and completed one formal batch. The COCO test command used the validation split, as the standard test-dev split has no labels for local evaluation. Python task methods use the public model's native setup. |
| Configuration | `base/detector/runtime/recipes.py` resolves the presets in `conf/config.yaml`. The former Nano recipe path still resolves to the 384-pixel detection config and accepts the explicit CPU accelerator override. The named segmentation Nano recipe resolves to the 312-pixel model from outside the checkout. |
| Experiments | The official results command opened both Nano executions and the Medium execution through the historical paths and their current locations. The saved precheck success and failure pass the central four-sample, 120-second check. The named launcher now records `stopped` when the fit process exits successfully without writing artifacts. Its results command still exposes the saved precheck report. |
| Docs, scripts and tests | The [checkout structure and task guide](code/website/source/resources/project_structure.md) describes the direct command-line precheck. MkDocs generated the documented URL using the newly built wheel and resolved the public API references. All 12,066 tests collected. The command-line, training and launcher suite passed 247 cases, with one skipped. All 10 launcher tests passed after the artifact-status fix. |

The retained Nano and Medium reports use the same eight validation images for checkpoint selection and to reproduce the stored scores under the archived GPU settings. The CPU check was a public-interface check and used different evaluation settings. Model performance comparisons require a separate representative evaluation set.

## Verify a copied template

Follow the [environment and resource guide](environment/README.md). Run `python -IS .everresearch/maintain.py check` in the project root. Then use the documented entry point with a small representative input and read back its output. The evidence above describes the reference checks. Measure throughput on the intended model, inputs and hardware before estimating a complete run.

## Recover the upstream source revision

The preserved upstream checkout was identified as [`59deab526f4efd43f3a536d1faa5035fd37f3c36`](https://github.com/roboflow/rf-detr/commit/59deab526f4efd43f3a536d1faa5035fd37f3c36), with Git tree `f8e6eb4e8cafee28539bea90f70812f75e494b31`. The original local checkout record is unavailable. Comparing unchanged files by Git blob ID against 100 first-parent upstream commits gave this revision 286 matching files, including 200 Python files. The previously attached November 21 revision matched 278 files, including 194 Python files, and differs at 30 paths.

The relocated [checkpoint weight loader](../models/detection_transformers/weights.py) matches the blob that first introduced query padding in the recovered revision. The relocated [Objects365 reader](../datasets/detection_data/objects_dataset.py) and [its regression test](../tests/product/datasets/formats/test_objects_dataset.py) match the same revision. The [next upstream commit](https://github.com/roboflow/rf-detr/commit/acfbb7546121d99649a72e0638b0896e8afb8fcd) changed both Objects365 files. This places the retained files at the intervening commit in upstream history. All 616 archived file paths, contents and Git modes match that commit's tree.
