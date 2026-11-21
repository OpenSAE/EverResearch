# Tasks

| Command | Inputs, computation and output |
| --- | --- |
| `python main.py colmap --scene_dir PATH` | Predicts camera and depth from `PATH/images/` and writes a COLMAP reconstruction bundle. `--use_ba` also tracks observations and invokes COLMAP bundle adjustment. `read-colmap` restores the original filenames for downstream tools. |
| `python main.py viser --image_folder PATH` | Predicts cameras and point geometry for a local scene and serves an interactive visualization. |
| `python main.py gradio` | Accepts image or video uploads and caches predictions and generated GLB files for the upload session. |
| `torchrun --nproc_per_node=4 main.py train` | Composes a Hydra recipe, fine-tunes or validates the selected model, and records experiment metadata, logs and checkpoints. |

COLMAP, Viser and Gradio check a representative scene input before loading model weights. Shared-camera bundle adjustment also verifies that original image dimensions agree. The training launcher checks declared dataset roots, the configured checkpoint and device availability before initialization. The standalone `python main.py precheck --image-folder PATH` decodes a representative input without loading model weights.

The [configuration reference](conf.md) covers the recipe. The [Fern experiment report](experiment.md) links the saved reconstruction and its measured readback.
