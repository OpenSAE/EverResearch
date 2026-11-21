# SAM 2 project guide

## Purpose and features

Find the prediction interfaces, research commands, inputs and experiment results.

## Scope

Use this guide to run SAM 2 or maintain its datasets, models, tasks and examples.

| Location | Use |
| --- | --- |
| [`base/`](base.md) | Public imports, runtime configuration and training launch. |
| [`conf/`](conf.md) | Image defaults and published Hydra recipe names. |
| [`datasets/`](datasets.md) | RGB images, video-object training mixtures and SA-V annotations. |
| [`models/`](models.md) | SAM 2 construction, Hiera backbones and checkpoint loading. |
| [`tasks/`](tasks.md) | Image prediction, video tracking, training, evaluation and benchmarking. |
| [`data/`](datasets.md) | Sample image and video inputs, training splits and local checkpoint paths. |
| [`scripts/`](tasks.md) | Thin entry points and interactive notebooks. |
| [`experiment/`](experiment.md) | New results and their effective settings. |
| `assets/` | Reference figures and supporting resources. |
| [`tests/`](code/README.md#local-checks) | Regression tests for image prediction, VOS and training configuration. |
| [`third_party/`](../third_party/meta_web_demo/README.md) | Upstream web demo and Docker instructions. |

See the [execution environment](environment/README.md) for installation and lightweight validation.

See the [maintenance and verification record](maintenance.md) for local migration and test evidence.
