# Whole-project maintenance record

## Purpose and main function

Map the project layout, public depth and camera commands, and observed validation.

## Scope of application

Use when preparing model, scene, or benchmark inputs and evaluating the recorded results.

The maintenance work retained the public commands, package imports and SOH workflow. Bind an interpreter and resource paths suitable for the copied project.

| Area | Implemented change and verified evidence |
| --- | --- |
| Runtime and interfaces | Moved the CLI, Python interface, services and runtime to `base/depth_anything/`. Verified the existing `da3` command, package imports, and the SOH configuration preview. |
| Datasets | Moved media handling and tensor input processing to `datasets/media/`, and six reader implementations to `datasets/benchmark/`. The SOH pair was read in source order and the six benchmark IDs registered. |
| Models | Moved the depth architecture and backbone to `models/model/` and `models/backbone/`. The seven presets load under their existing names. A random-initialized DA3 Small model produced depth on CPU. The original acceptance archive documents the two earlier official-checkpoint executions. |
| Tasks | Moved prediction, evaluation and streaming computation to `tasks/`. Named inference verified a successful automatic precheck and a separate invalid-resolution rejection before prediction. Evaluation rejected missing ETH3D data and streaming rejected its missing SALAD submodule before creating output. |
| Configuration | Added `conf/config.yaml` as the inference default entry and moved the model, benchmark and streaming preset branches underneath their owner paths. Inference, benchmark and streaming printed their actual effective values. |
| Experiments | Preserved both original SOH executions and their reproducibility evidence in an archive. Re-recorded manifests and read their original prediction arrays. The bounded DA3 Small verification used two SOH images and processing resolution 56. The NPZ depth read back as `(2, 28, 56)` with finite values. |
| Packaging and docs | Moved the notebook and streaming entry scripts to `scripts/`, SALAD to `third_party/`, docs to `doc/`, and the README figures into their asset group. Built wheel, source archive and editable wheel from locally available build dependencies. Imports from the built wheel loaded the published model paths and recipes. Nine repository tests passed. |

[Project and source guide](code/guides/project.md) ·
[Original SOH results](../assets/history_experiment/soh_scene_geometry/README.md)

## Bounded verification

The DA3 Small checkpoint was generated locally with `torch.manual_seed(0)`
and `DepthAnything3("da3-small").save_pretrained(...)`. The successful run used
`--device cpu --process-res 56 --export-format npz --experiment export_verification`.
The corresponding failed run used `--process-res 0`. Review their records
with `da3 results experiment/soh/da3_small/inference/export_verification`.
This compares software behavior using the bundled SOH images. The prior
acceptance archive contains the original model weights' provenance and
released-model results.

Full benchmark execution requires the prepared benchmark data. Full streaming
execution requires the SALAD checkout, optional streaming dependencies and
local weights. The benchmark and streaming workflows retain their documented
workspace and output-directory conventions.

## Follow-up acceptance

| Area | Current behavior and evidence |
| --- | --- |
| Runtime | Named inference launched from an unrelated working directory with the editable installation resolves to this checkout. The rebuilt wheel locates the checkout from a nested directory and requires an explicit export destination when used elsewhere. |
| Datasets | The normal CLI selected `000.png` followed by `010.png` from the bundled SOH data. The video precheck extracted one frame from the bundled Unitree example. |
| Models | Removed duplicate YAML anchors in the combined model presets that prevented importing the Python API. Compared all seven parsed presets to the original standalone files and verified equal configuration values. |
| Tasks | A named inference run used the selected model for a one-view prediction and NPZ readback before the full pass. The invalid-resolution run stopped before trying to load the intentionally unavailable checkpoint. The benchmark entry rejected missing ETH3D data and streaming rejected the absent SALAD checkout before creating their requested outputs. |
| Configuration | Confirmed a normal inference configuration preview, benchmark overrides for ETH3D pose evaluation, and the TUM streaming preset. |
| Experiments | `da3 results experiment/soh/da3_small/inference/precheck_verification` opens the new successful execution with its precheck report. The saved NPZ contains finite depth for both SOH inputs with shape `(2, 28, 56)`. The central experiment check passed six records, and the central precheck check accepted the success and rejection pair with one sample. |
| Packaging and docs | Built a source archive and wheel offline, imported the public API, CLI, benchmark and backend from the extracted wheel, and ran the repository tests. All eleven passed. |

The verification used a random-initialized DA3 Small checkpoint recreated
with the seed described above. It exercised the software path on CPU.
The released DA3 Nested Giant Large weights are absent from the local
Hugging Face snapshot. The earlier released-model results remain available in
the project archive. Full benchmark scoring, streaming alignment and the
interactive Gradio interface still require their data, weights or optional
dependencies.

## Explicit inference commands and default paths

| Area | Verification and outcome |
| --- | --- |
| Runtime and interfaces | The CLI now forwards `--ref-view-strategy` from `image`, `images`, `colmap` and `video`. Inference previews from the checkout and its parent select the same default local export directory. Explicit relative output paths use the caller's working directory. |
| Datasets | `da3 images` read the two bundled SOH images with the local CPU checkpoint. The benchmark CLI identified the missing ETH3D data root before model load. |
| Models | A seeded DA3 Small checkpoint exercised model construction and inference on CPU. The installed API imported all seven model recipes from the wheel. |
| Tasks | All four explicit inference commands passed their options to the inference service in the regression tests. The HTTP endpoint passed reference-view and ray-pose options to a controlled model and rejected zero resolution before model load. Invalid video sampling frequency is rejected before creating the export directory. Streaming rejected the missing SALAD checkout. |
| Configuration | The default local export directory and the built-in streaming output and weight paths resolve from the checkout when available. The TUM configuration preview verified the selected preset, paths and chunk size from the parent directory. |
| Experiments | The direct CPU export returned two finite depth maps with shape `(2, 28, 56)` through NPZ readback. `da3 results` read the earlier released-model runs. The central check accepted all six recorded executions and the named inference precheck success and rejection pair. |
| Packaging and docs | Built the wheel and source archive offline and imported the published CLI, API, backend and streaming module from the wheel. Seventeen repository tests passed. The current editable environment uses `python -m depth_anything_3.streaming`. |

Full benchmark scoring requires prepared benchmark datasets. Full streaming
alignment requires the streaming dependencies, local weights and SALAD checkout
when loop detection is enabled. The CPU check used randomized weights and
verified data flow and artifact readback. See the archived published-model
runs for model results.

## Gallery readback after the experiment migration

The standalone gallery and backend gallery accept direct exports and named
experiment executions. Both list the saved SOH scene and serve its model,
cover, and two depth preview images. The four files returned by each service
match the original archived bytes. The preview archive remains the canonical
location of numbered frames in the recorded execution. The gallery regression
test covers direct exports and reads numbered previews from that archive.

## Verify a copied template

Follow the [environment and resource guide](environment/README.md). Run `python -IS .everresearch/maintain.py check` in the project root. Then use the documented entry point with a small representative input and read back its output. The evidence above describes the reference checks. Measure throughput on the intended model, inputs and hardware before estimating a complete run.
