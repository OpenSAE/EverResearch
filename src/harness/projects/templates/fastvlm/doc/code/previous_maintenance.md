# Source layout and maintenance record

## Scope

The assessment started from upstream revision `6f7b131` and the checked-out files. The documented PyTorch image-prompt example provided the software acceptance path. Published weights, research data, training, Apple hardware, and live serving were outside the software check.

## Directory disposition

| Directory or files | Consumers and disposition |
| --- | --- |
| Root `README.md`, `pyproject.toml`, `predict.py`, `get_models.sh`, working instructions and legal files | Retain existing locations for documented commands, Python package metadata, checkout setup and licenses. The public inference script now delegates to the runtime and the download helper anchors its destination to the checkout. |
| `.agents/skills/` | Locally linked skills and the generated project entry. The existing hook and symlinks point to ResearchHarness. |
| `.github/workflows/`, `tests/` | The workflow runs project checks. The Python tests verify inference interfaces and exporter tokenizer metadata using local fixtures. |
| `app/Configuration/`, `app/FastVLM App/`, `app/FastVLM.xcodeproj/`, `app/FastVLM/`, `app/Video/` | Retain Xcode's paths for build settings, SwiftUI and assets, project and scheme metadata, model runtime, and camera. The Xcode project uses synchronized groups for its source layout. The nested asset catalogs and scheme metadata follow Apple's component formats. The app helper downloads prepared model assets to a caller-selected folder. |
| `conf/`, `datasets/`, `models/`, `tasks/` | The new formal command reads the JSON recipe, reads a real local input format, loads the checkpoint and generates an answer through these components. The wheel maps these paths into the `fastvlm` namespace. |
| `fastvlm/` | Houses the CLI, project runtime and result I/O. The installed entry and original script share the implementation. |
| `docs/`, `doc/` | The existing media stays at the paths embedded by the root and app README files. The new index maps source, configuration, tasks, run results and verification. |
| `llava/` | Preserve installed imports, shared constants, templates, image preprocessing and serving utilities. The primary task shares this code with inherited utilities where the input contracts match. |
| `llava/model/` | Keep the existing tokenizer and checkpoint builder, multimodal composition and standalone delta/consolidation tools with their public import paths. The tools write to paths supplied by their callers. |
| `llava/model/language_model/`, `llava/model/multimodal_encoder/`, `llava/model/multimodal_projector/` | Language model files implement distinct underlying architectures. The encoder selector dispatches shared model behavior to CLIP or MobileCLIP, whose local model config is packaged. Projector selection stays in its own builder. |
| `llava/serve/` | Keep the interactive command, controller, workers, registration, Gradio examples and service probe as the existing service workstream. They retain their native diagnostic and conversation logging contracts. |
| `llava/train/` | Keep upstream trainer, Qwen training implementation, low-memory and xFormers launchers and attention patches available at established module paths. Training writes to its configured output directory. |
| `model_export/` | Retain the documented Apple Silicon workflow and version-specific MLX-VLM patch. Export writes to the selected checkpoint directory and uses a private temporary trace. |
| `checkpoints/`, `experiment/`, `tmp/`, interpreter and build caches | Downloaded weights, saved run results, transient local checks and generated caches are treated as data and build outputs. The public loader accepts explicit weight locations. Result directories are generated on completion. |

The recursive source scan covered direct files in each physical directory, including the nested model, serving example, Xcode and documentation trees. The largest groups of active direct files were the repository root, `doc/`, and `llava/serve/`. Each stayed at or below ten direct files. The supplied local skill symlinks were inspected as links to the separate worktree.

## Seven maintenance checks

| Area | Entry and finding | Work and verification |
| --- | --- | --- |
| Runtime | Originally `python predict.py --help` imported the full dependency tree and stopped at the missing `timm` module. Inference forced MPS. | The same script and the installed command use the runtime to resolve the recipe, validate input, select a device and invoke generation. Help and preview execute with the standard library. The offline CPU smoke test passed through the real loader and generation code. |
| Data | The original CLI opened a local image and passed its original dimensions to LLaVA preprocessing and generation. The user provides the sample and there are no task labels or splits. | The image reader keeps RGB conversion and records the byte digest and dimensions. Tests checked an 8 × 5 grayscale fixture and an actual inference smoke test used a separate 13 × 7 synthetic RGB sample. |
| Model | The project exposes PyTorch checkpoints through the inherited LLaVA builder and Apple models through the export and Xcode workflows. Inference renamed `generation_config.json` on disk before loading. | The PyTorch task passes an in-memory generation config, and the loader accepts explicit CPU precision and single-device placement. A local miniature LLaVA-Qwen2 with a CLIP tower exercised loading and generation. The exporter tests check stable image token identity when re-exporting. |
| Task | LLaVA places an image marker inside a conversation template, processes the image as required by the selected checkpoint and decodes generated tokens into one answer. | The formal command calls the same template, preprocessing, tokenizer and generation interfaces through the image prompt task. The application, serving, training and export workflows keep their independent public entry points. |
| Configuration | The original options came from inline parser defaults. | The public command consumes `conf/config.json`, displays the resolved options, and accepts both styles of existing multiword flags. Tests confirm preview from a separate working directory, failure before loading and exact agreement between recipe and parameter documentation. |
| Experiment | The original command returned its answer via standard output. | The answer remains on standard output. Its manifest path goes to standard error. The test suite repeated inference with the same experiment name and read both results through `--read-result`, matching image identity. The smoke test also read back the generated answer. |
| Supporting assets | Pytest originally collected the service probe as a test module, where dependency imports failed. The checkpoint helper resolved output from the caller's directory and could continue after a failed download. | Root test discovery now covers the dedicated regression tests. The offline shell fixture confirmed six archive names, checkout-root output, cleanup, and propagation of a simulated downloader error. Shell syntax and exporter help were checked. The wheel included the recipe, MobileCLIP configuration and bundled example images. |

## Local validation evidence

- `python -m pytest -q` exercised CLI behavior, fixture identity, result compatibility and exporter token metadata. Root collection discovered only the two project test files.
- The software smoke run used Python 3.12.15, PyTorch 2.11.0 CUDA build executing on CPU, Transformers 4.48.3, Tokenizers 0.21.0 and timm 1.0.15. The network was disabled for Hugging Face loaders. Both runs from an unrelated working directory used the same locally generated model and 13 × 7 image. With temperature zero and at most two new tokens, each produced `shape red` and a separate manifest in the project checkout. Readback matched the answer, digest, dimensions and selected device. The test checkpoints and run folders were transient engineering inputs and outputs.
- The Apple demo requires Xcode and compatible hardware. Core ML conversion and MPS execution require their respective environments. Inherited LLaVA training and live serving were traced through source. Their runtime behavior requires their historical recipes or a live service.

## Published checkpoint acceptance checks

| Area | Entry, changes and evidence |
| --- | --- |
| Runtime | ResearchHarness bound the isolated interpreter and external COCO root. Its `run` command used the checkout's `predict.py`. The editable `fastvlm` command used a relative image from the data directory. Both wrote their manifests under the same checkout. |
| Data | The published COCO `val2017` JPEGs `397133` and `252219` each went through the existing RGB image reader. The new `--dataset coco_val` option preserves the actual source in each result. Independent reads matched both byte digests and original dimensions. |
| Model | The default local path loaded Apple's 0.5B Stage 3 PyTorch release with MobileCLIP at 1024 pixels and the Qwen2 model. Both runs completed on CUDA. The acceptance record captures digests for the Apple archive and the loaded safetensors file. |
| Task | The default `image_prompt` task used `qwen_2` and `Describe the image.` through the public inference commands. The first description identifies a kitchen and hanging pots. The second identifies pedestrians and a cart on the street. |
| Configuration | `--show-config` resolved the image from the harness binding and the default checkpoint from the checkout. The recipe and parameter page include the optional dataset name. Tests cover its default, explicit value and path traversal rejection. |
| Experiment | Real predictions now group under `coco_val/fastvlm/0_5b_stage3`. Each execution stores its own configuration and manifest. The public reader reproduced stdout and both image identities. Tests also check the equivalent layout for the 1.5B Stage 2 release and retain readback by manifest path. |
| Supporting assets | The isolated Python 3.10 suite collected and passed 18 tests. The environment guide documents the official CUDA 12.8 wheels used on Blackwell. The local acceptance record preserves exact commands, source changes, environment and checksums. |

The [published checkpoint acceptance](../experiment.md#published-checkpoint-acceptance) links both manifests and gives the steps to repeat the runs. These observations cover PyTorch image-prompt inference on the two COCO inputs.
