# Project maintenance record

## Purpose and main function

Map geometric reconstruction, tracking and training code and record the available evidence.

## Scope of application

Use when preparing image scenes, published weights and reconstruction or training workloads.

| Responsibility | Change and verification |
| --- | --- |
| Runtime | The source launcher selects the same application modules as the installed `vggt` command. The wheel preserves older Python imports. |
| Datasets | The Co3D and Virtual KITTI 2 implementations have separate reader directories. The existing tests exercise split annotation loading, missing input, read-only discovery and explicit camera lists. The Fern precheck decoded a representative frame from the four registered input files. |
| Models | The geometry transformer, prediction heads and trackers use one package mapping for source and wheel builds. The older `vggt.models.vggt.VGGT` import resolves to the current class. |
| Tasks | COLMAP, Gradio, Viser and fine-tuning reach their separate implementations. Missing scene images and training roots stop before weights are loaded. The COLMAP geometry regression covers two preprocessing resolutions. |
| Configuration | Training reads `conf/config.yaml` and its shared dataset settings. Source and installed configuration previews preserve the camera and depth setup. The older `default` recipe selector still loads this configuration. |
| Experiments | The three existing Fern reconstructions each have a manifest and lossless native archive. The latest archive reopened with four images and four cameras, 22,484 points and a maximum reprojection error of 0.00002602 pixels. Training record tests use synthetic checkpoints. |
| Supporting assets | Bundled image scenes and videos retain their original media names, and source launchers are under `scripts/examples/`. The full suite collected and passed 20 tests. |

The recorded Fern reconstruction used historical pretrained inference. The maintenance round verified its actual stored outputs and used local fixtures for software behavior. Fresh weighted inference, bundle adjustment and distributed training require their actual resources.

## Verify a copied template

Follow the [environment and resource guide](environment/README.md). Run `python -IS .everresearch/maintain.py check` in the project root. Then use the documented entry point with a small representative input and read back its output. The evidence above describes the reference checks. Measure throughput on the intended model, inputs and hardware before estimating a complete run.

## Recover the upstream source revision

The preserved upstream checkout was identified as [`a288dd0f14786c93483e45524328726ab7b1b4ce`](https://github.com/facebookresearch/vggt/commit/a288dd0f14786c93483e45524328726ab7b1b4ce), with Git tree `0c6815bb33b15442e098b89245ec8e0ecfcc672e`. The original local checkout record is unavailable. The relocated [token aggregator](../models/geometry_transformer/models/token_aggregation.py) is byte-identical to the optimized aggregator introduced in the [preceding upstream commit](https://github.com/facebookresearch/vggt/commit/9e4fa662a8893ed348d048e8b57816c12593448b). The two upstream commits have identical tracked files outside `README.md`. The May 18, 2026 VGGT-Omega announcement in the [retained README](../README.md#updates) was added by the archived revision and identifies it among the two. All 171 archived file paths, contents and Git modes match that commit's tree.
