# RF-DETR checkout documentation

## Purpose

Use this index to locate the normal entry points and the code responsible for data, models, training, evaluation, inference and deployment.

## Start here

- [Project structure and training launcher](code/website/source/resources/project_structure.md) maps commands to components and explains how to preview, launch and read a named experiment.
- [Installation and environment](environment/README.md) describes checkout setup, data preparation and local verification.
- [Training recipes](conf.md) explains recipe selection, overrides and the parameter reference.
- [Experiment results](experiment.md) explains how to create and read a named training run.
- [Maintenance record](maintenance.md) records the layout migration and its verification.

## Browse a component

| Location | Responsibility and entry point |
| --- | --- |
| [Package source](../base/detector/) | The installed model, prediction and export interfaces. The console entry is `rfdetr`; the module entry is `python -m rfdetr`. |
| [Datasets](../datasets/detection_data/) | Build samples and splits for [COCO, Objects365, Roboflow, YOLO and WebDataset](code/website/source/learn/train/dataset_formats.md). |
| [Models](../models/detection_transformers/) | Build detector backbones, heads, matching and loss components. [Public variants](code/website/source/learn/pretrained.md) define the released models and default weights. |
| [Tasks](../tasks/) | Train and evaluate through the [Lightning API](code/website/source/reference/training.md) and the public RF-DETR model. |
| [Shared support](../base/utilities/) | Package utilities used by the build, task and API layers. |
| [Configuration](../conf/config.yaml) | Checkout recipes and component identities used in experiment paths. |
| [Scripts](../scripts/) | Named training, checkpoint generation, documentation operations and executable cookbook examples. |
| [Tests](../tests/) | Product behavior, integration scenarios and test fixtures. See the [contributor guide](../.github/CONTRIBUTING.md#test-driven-development) for the commands used by CI. |
| [Documentation assets](../assets/documentation/) | Media, styles, templates and root files for the published site. |
| [Workflows](../.github/workflows/) | Continuous integration, package builds and versioned documentation deployment. |

Build the site from the checkout using a documentation environment with RF-DETR installed from a wheel. MkDocs reads the public module paths from that installation to generate the API reference. The [documentation build workflow](../.github/workflows/ci-build-docs.yml) shows the package and dependency installation command. Run `python -m mkdocs build -f scripts/documentation/site_config.yaml` in the same environment. The site is written to `.site/`.
