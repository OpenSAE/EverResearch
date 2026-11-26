# MathVista verification and run choices

## Purpose and main function

Record the evidence for the maintained evaluation commands and estimate the
complete testmini workload for each stage.

## Scope of application

These measurements use MathVista revision `24b1478`, the official
`AI4Math/MathVista` dataset, and the local Qwen2.5-VL-3B-Instruct checkpoint
documented in the [environment guide](environment/README.md#local-qwen-weights).
The complete workload is one sequential pass over the 1,000 official testmini
samples. The first ten problem IDs, 1–10, were used for the timed runs.
Their public data and image bytes were fetched in 4.75 s before timing.

## Measured stages and full-run choices

| Stage and compute unit | Measured sample | Estimate for 1,000 | Product |
| --- | --- | --- | --- |
| Generation, one official image and question per request | All 10 completed. Cold process wall time was 21.481 s including 6.879 s to load weights and 2.577 s for the first request. The warm repeat took 15.932 s and reproduced the same responses. Its last nine requests averaged about 0.81 s each. | **11–18 min** on one RTX 5090 with BF16 and a 128-token cap. The sample mean projects to about 14 min. Image and output lengths drive variation. | Generation records |
| Extraction, one generated response | All 10 completed. Local rules handled one response. The remaining nine used Qwen with a 32-token cap. The initial 6.656 s includes 1.631 s to load weights and 0.465 s for the first model request. The repeat took 5.599 s, with 1.411 s for weight loading. Its other eight requests took 0.044–0.081 s each. | **45–85 s** on the same GPU. The share of responses needing the model and their lengths drive variation. | Extraction records |
| Scoring, one extracted answer plus group aggregation | All 10 completed in 0.511–0.607 s on an AMD Ryzen 7 7800X3D, including startup, label readback and scoring. Four answers were correct. The independent 1,000-row published random baseline also scored locally in under one second. | **1–3 s** on the same CPU with local labels and outputs. | Score report |

Qwen peak CUDA allocation after the first warm image request was 7.24 GiB.
Four of the ten image responses reached the 128-token cap. Full estimates assume
a single process and one item per batch, with the normal 100-item checkpoint
interval. The 1,000-item Qwen workload remains available for selection.
Dataset acquisition is outside the wall estimates.

The independent generation and extraction prechecks each verified problem 1
with checkpoint inference in 6.913 s and 5.065 s, including startup. The scoring
precheck calculated and read back problem 1 using its local label in 0.473 s. Formal commands ran the same one-problem gates
automatically. Failed prechecks blocked missing weights, missing responses, and
missing predictions before their respective task loops began.

## Reproduce the timed sample

Activate the [project environment](environment/README.md#local-qwen-weights).
The commands select the first ten examples through the official split loader.
They use the measured model, token limits, and per-stage process cap. The
reference timing excluded acquisition of the input images.

```sh
base=experiment/math_vista/mini_test
generated="$base/generation/qwen_sample/artifacts/predictions.json"
extracted="$base/extraction/qwen_sample/artifacts/predictions.json"

timeout --signal=INT --kill-after=15s 285s "$qwen_python" -m mathvista generate \
  --model qwen_vision --test_split_name testmini --max_new_tokens 128 \
  --max_num_problems 10 --save_every 1 --run-purpose qwen_sample --rerun
timeout --signal=INT --kill-after=15s 285s "$qwen_python" -m mathvista extract \
  --extractor qwen_vision --input "$generated" --max_new_tokens 32 \
  --max_num_problems 10 --save_every 1 --run-purpose qwen_sample
timeout --signal=INT --kill-after=15s 285s "$mathvista_python" -m mathvista score \
  --input "$extracted" --ground_truth_file_path testmini.json \
  --max_num_problems 10 --run-purpose qwen_sample
```

For a standalone precheck, use the same input with `--precheck-only`.
New runs write configuration and result records under
`experiment/math_vista/mini_test/<stage>/`.

## Run the complete testmini workload

Use the full official split for generation and pass each stage's predictions to
the next command. Run the precheck first in each stage using the same input and
model settings.

```sh
base=experiment/math_vista/mini_test
"$qwen_python" -m mathvista generate --model qwen_vision \
  --test_split_name testmini --max_new_tokens 128 --run-purpose qwen_benchmark
"$qwen_python" -m mathvista extract --extractor qwen_vision --max_new_tokens 32 \
  --input "$base/generation/qwen_benchmark/artifacts/predictions.json" \
  --run-purpose qwen_benchmark
"$mathvista_python" -m mathvista score --ground_truth_file_path testmini.json \
  --input "$base/extraction/qwen_benchmark/artifacts/predictions.json" \
  --run-purpose qwen_benchmark
```

## Other workflow evidence

Both official splits were sampled through the dataset loader. The first
`testmini` image decoded at 1514 × 720 with a public label. The first `test`
image decoded at 981 × 650. Scoring the complete `test` split needs private
answer labels. Azure, Bard, and Claude execution needs provider access. The
optional preparation utilities need their own models or services.

The full published testmini random baseline returned 179 correct out of 1,000.
Every normalized prediction and correctness flag matched the archive.
The archived 74 result files, 68 figures, 5 source data files, and 3 prepared
input files matched their Git blobs at revision `24b1478`. Current score JSON
represents accuracy as a numeric fraction. Published JSON retains its original
percentage strings.
