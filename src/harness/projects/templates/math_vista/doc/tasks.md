# MathVista evaluation and preparation

## Purpose and main function

Run the three MathVista evaluation stages, reproduce published scores, and locate
the preparation commands.

## Scope of application

These commands use the environment described in [Environment and setup](environment/README.md).
Run them from the project root, or use the installed `mathvista` command with
`MATHVISTA_PROJECT_ROOT` set.

## Generate responses

```sh
python -m mathvista generate --test_split_name testmini --precheck-only
python -m mathvista generate --test_split_name testmini --max_num_problems 10
```

Generation samples the selected split, builds a prompt, and calls the selected
service. The configured Azure deployment takes precedence over `--model`.
Select `--shot_num`, `--use_caption`, and `--use_ocr` for prompt changes.
`--shot_type code` executes the returned Python with the current user's permissions.
Use that mode only with code you trust and in an isolated environment.

Select `--model qwen_vision` for local image and text inference using
the [local checkpoint setup](environment/README.md#local-qwen-weights).
Use `--max_new_tokens 128` to reproduce the profiled solution generation.
Qwen uses deterministic decoding, one input at a time. Its image processing
budget is set by `catalogs.model.qwen_vision.max_pixels` in `conf/config.toml`.

## Extract answers

```sh
python -m mathvista extract --input experiment/math_vista/mini_test/generation/benchmark/artifacts/predictions.json --precheck-only
python -m mathvista extract --input experiment/math_vista/mini_test/generation/benchmark/artifacts/predictions.json
```

The extractor uses direct matches, numeric conversion, or the configured model.
Select `--extractor qwen_vision --max_new_tokens 32` to use the local model. `--quick_extract` also recognizes the original quoted-answer pattern.
`--results_file_path` preserves the legacy in-place interface.

## Score predictions

```sh
python -m mathvista score \
  --input assets/history_experiment/published/files/random/output_random_guess.json \
  --ground_truth_file_path testmini.json --run-purpose published_reproduction
```

This uses published predictions and local MathVista labels. The result directory
contains `artifacts/predictions.json`, `artifacts/scores.json`, the precheck report,
and the run's effective configuration. Select `--precheck-only` to evaluate one
input and stop. Select `--max_num_problems` to bound the formal score. Scores
include the average and per-category counts and fractions.

## Prepare image context

The captions and OCR files used in publication are under
[visual context](../assets/prepared_data/visual_context/README.md). The
`caption-bard`, `caption-vision`, and `ocr` commands regenerate the associated
inputs when the optional dependencies, images, and service credentials are available.

## Read historical results

The [published archive](../assets/history_experiment/published/README.md) retains
the original predictions and scores. The scripts under `scripts/generation/`
and `scripts/published/` preserve the original recipe settings and use working
copies under `tmp/legacy_reproduction/`. The old `evaluation.*` module imports and
`models.*` adapters remain available after installation. The checkout commands
formerly run from `evaluation/` now run through `python -m mathvista`.

Standard runs use `experiment/math_vista/<split>/<stage>/<purpose>/`.
Use a descriptive `--run-purpose` for independent runs. Explicit legacy
output paths retain their original JSON format.
