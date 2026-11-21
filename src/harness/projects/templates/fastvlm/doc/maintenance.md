# FastVLM project maintenance

The checkout is at `/path/to/workspace/FastVisionLanguage`. The original `/path/to/workspace/FastVLM` address resolves to the same Git working tree, and the existing Python and COCO data bindings still resolve. [Earlier maintenance evidence](code/previous_maintenance.md)

| Scope | Implementation and evidence |
| --- | --- |
| Base | `main.py` and the installed `fastvlm` command share `base/fast_vlm/commands.py` and `runtime.py`. Configuration preview and result readback work from another working directory. |
| Dataset | `datasets/user_image/` preserves RGB conversion, SHA-256 and original dimensions. The two COCO results retain their original paths and input identities. |
| Model | `models/fast_vision/` selects and loads checkpoints; the architecture, language backends, image encoders and projector live under `models/model/`. The installed package loads the relocated MobileCLIP configuration. The local published checkpoint directory retains tokenizer and configuration files, while the actual weight file is absent. |
| Task | `tasks/image_prompt/` generates the answer. Its automatic gate in `tasks/precheck/` checks one image, executes one greedy token and verifies result readback. A miniature CLIP and Qwen2 checkpoint completed CPU inference. A missing checkpoint was rejected before generation. Inherited training and serving are available via their existing module commands. The Apple export and demo require their documented environments. |
| Configuration | `conf/config.json` supplies command defaults and declares result group names. `conf/models/model/config.json` supplies MobileCLIP's encoder settings. The test suite checks command defaults against the parameter page. |
| Experiment | Two prior COCO runs moved to the new execution paths, with unchanged prediction files. Both pass the central experiment check and open through their original manifest addresses. The original files, logs and actual execution recipe are stored together. [Original acceptance archive](../assets/history_experiment/coco_acceptance/README.md) |
| Supporting files | Published weight downloads use `scripts/models/get_models.sh`. Figures, examples, upstream notices and the MLX-VLM patch have separate asset groups. The original Xcode project tree is under `third_party/apple_demo/`. The lightweight test suite passes and an offline wheel build verifies package data. |

## Path changes

| Previous location | Current location |
| --- | --- |
| `fastvlm/` and shared `llava/` source | `base/fast_vlm/` and `base/language_vision/`. Public package names are mapped by the project build. |
| `llava/model/` | `models/model/`. The MobileCLIP model settings are in `conf/models/model/config.json`. |
| `llava/train/`, `llava/serve/` | `tasks/train/`, `tasks/serve/`. The Gradio examples are in `assets/examples/serving/`. |
| `datasets/user_image.py`, `models/fastvithd.py`, `tasks/image_prompt.py` | The image reader, checkpoint adapter and generation task are implemented in named component directories. |
| `checkpoints/`, `get_models.sh` | `data/checkpoints/` and `scripts/models/get_models.sh`. Explicit references to existing migrated local checkpoints resolve through the command. |
| `model_export/` | Export implementation in `tasks/image_prompt/`, guide in `doc/code/apple_silicon/`, MLX patch in `assets/integration/apple_mlx/`. |
| `app/`, `docs/` | Xcode project in `third_party/apple_demo/` and figures in `assets/documentation/figures/`. |
| `ACKNOWLEDGEMENTS`, `LICENSE_MODEL` | `assets/licensing/upstream/files/`. |
| `experiment/coco_val/fastvlm/0_5b_stage3/` | The two executions are in `experiment/coco_val/fast_vision_small_stage3/`. The acceptance archive preserves the original paths and file contents. |

The current source command is `python main.py`. The original `predict.py` launcher is preserved in the COCO acceptance archive. Use the same command options with the current source entry. The historical research runs predate automatic precheck. Smoke tests validate the current precheck, and the original smoke inputs and prediction records are distinct from the published COCO results.

## Current checkout checks

| Scope | Observed behavior |
| --- | --- |
| Base | The checkout command ran from outside the repository. A separately installed wheel reported the missing workspace before inference and saved a prediction after setting `FASTVLM_WORKSPACE`. |
| Dataset | Both COCO readbacks matched the SHA-256 digest and dimensions of the original JPEG. The LLaVA launchers now share the JSON conversation and image reader in `datasets/supervised/`. |
| Model | The miniature CLIP and Qwen2 checkpoint loaded on CPU for generation and the training check. The installed Python environment exposes CUDA. The published checkpoint directory lacks the weights needed for a fresh published-model run. |
| Task | The normal inference command completed with a one-token precheck and rejected a missing checkpoint before generation. The Qwen launcher trained for one optimizer step with valid labels and rejected a fixture whose template masked every target. Interactive chat and the standalone PyTorch worker generated text on CPU. The worker rejected an image marker without an attachment. Apple export reported the missing MPS device. |
| Configuration | The main recipe and parameter page agree in the command test. The encoder page links the MobileCLIP configuration used by the loader. |
| Experiment | The current inference command and historical COCO records open with `--read-result`. The central precheck checker accepted the current successful and rejected inference runs. The training smoke check inspected the trainer state and found one completed step with finite, positive loss. |
| Supporting files | The offline wheel included the supervised reader alongside the existing package mappings. The tests cover wheel workspace handling and inference validation without published weights. |

Live SGLang, Flash Attention and xFormers checks require their respective dependencies. Core ML conversion and the Swift application require an Apple environment. The checked training launcher continues to write its native artifacts to the requested location.
