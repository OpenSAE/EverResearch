# VGGT source layout

The project reconstructs camera poses, depth, points and point tracks from images. The same VGGT checkpoint serves the Python API and the visualization and export applications.

| Path | Purpose |
| --- | --- |
| `base/geometry_runtime/` | Command dispatch, training configuration composition, installation mappings, compatibility imports and runtime records. |
| `datasets/multi_view/` | Image tensor preprocessing, frame sampling and the shared training loader. |
| `datasets/common_objects_3d/reader/` and `datasets/virtual_kitti_2/reader/` | Co3D sequence annotations and Virtual KITTI 2 image, depth and camera inputs. Virtual KITTI 2 also has a data preparation script. |
| `models/geometry_transformer/` | VGGT architecture and heads, pretrained model loading, camera geometry and the tracking models used for bundle adjustment. |
| `tasks/reconstruction/`, `tasks/viewer/` and `tasks/fine_tune/` | COLMAP geometry export, Gradio and Viser application workflows, and distributed training and validation. |
| `tasks/precheck/` | Representative image decoding, shared-camera dimension verification and training resource validation. |
| `conf/` | The Hydra default recipe and shared dataset settings. |
| `assets/examples/` | Upstream image sets and videos consumed by the demo workflows. The native filenames are preserved inside each source bundle. |
| `scripts/examples/` | Standalone launchers and visualization imports carried forward from the original source layout. |
| `tests/` | Software checks for commands, dataset selection, checkpoints, reconstruction coordinates and result paths. |
| `experiment/` | Managed reconstruction bundles, effective configurations, output manifests and original execution evidence. |

From source, run `python main.py --help` for the available commands. The wheel exposes the same commands through `vggt` and keeps the documented API imports `vggt.models.vggt.VGGT` and `vggt.utils.load_fn.load_and_preprocess_images`. The checkout root is `/path/to/workspace/VisualGeometryTransformer`. The registered path `/path/to/workspace/VGGT` resolves to the same checkout.

The [fine-tuning guide](training.md) describes datasets, launch and checkpoint selection. The [environment guide](../environment/README.md) explains setup and the [reconstruction report](../experiment.md) links the recorded Fern results.
