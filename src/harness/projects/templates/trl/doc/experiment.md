# TRL training run choices

## Purpose and main function

Run the supported training recipes, check data and weights before a formal run, and estimate the duration of one full epoch.

## Scope of application

These choices use the pinned Zen dataset and tiny Qwen2 checkpoints on this machine. The estimated times apply to this CPU fixture workload. They depend on model size, sequence length, sampling settings, and hardware when the recipe changes.

## Run a recipe

```sh
export CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python main.py precheck --task sft --study input_readiness
python main.py run --task sft --study full_training
```

Replace `sft` with a task from the table. Choose a fresh descriptive study name per task. The launcher runs the same gate before the full epoch and stops before training if the gate fails. The gate runs the installed `trl` task in an isolated process, trains on about ten units, evaluates the official validation split, and opens a saved tensor. For a short end-to-end acceptance run, add `--max-steps 1` to `run`. The gate and bounded formal smoke run share a 280-second internal process budget. The timing harness applied an additional five-minute cap from the Python launcher’s startup.

### Resources and full workload

- Data comes from [`trl-internal-testing/zen`](https://huggingface.co/datasets/trl-internal-testing/zen) at revision `47aee340f33dd6161e2baa618240b8514666c822`. Every recipe has 17 training rows and 2 validation rows. The gate does not use validation rows for optimization.
- The trainable checkpoint is [`trl-internal-testing/tiny-Qwen2ForCausalLM-2.5`](https://huggingface.co/trl-internal-testing/tiny-Qwen2ForCausalLM-2.5) at revision `edca82771e1fad8f0b7ce110ffe770c682043fec`. Distillation uses the same checkpoint for its teacher. GRPO and RLOO use [`trl-internal-testing/tiny-Qwen2ForSequenceClassification-2.5`](https://huggingface.co/trl-internal-testing/tiny-Qwen2ForSequenceClassification-2.5) at revision `58b5b1655194e908b2af57189fccd4254b894f20` as the reward model.
- Measurements used one CPU process, one OpenMP thread, one numerical-library thread, zero data-loader workers, Python 3.12, PyTorch 2.10.0, Transformers 5.24.1, and TRL 1.20.0.dev0. All assets were cached before timing. Batch sizes and generation settings match the full-epoch choices.

| `--task` | Zen configuration | Batch | Gate train + validation | Gate wall time | Full epoch optimizer steps | Estimated full run |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `sft` | `conversational_language_modeling` | 1 | 10 rows + 2 | 10.3 s | 17 | 16–29 s |
| `dpo` | `standard_preference` | 1 | 10 rows + 2 | 8.4 s | 17 | 14–26 s |
| `reward` | `standard_implicit_prompt_preference` | 1 | 10 rows + 2 | 9.2 s | 17 | 14–24 s |
| `kto` | `standard_unpaired_preference` | 2 | 10 rows + 2 | 8.2 s | 9 | 14–25 s |
| `distillation` | `standard_prompt_only` | 1 | 10 prompts + 2 | 7.6 s | 17 | 12–22 s |
| `grpo` | `standard_prompt_only` | 2 | 10 prompts + 2 | 8.3 s | 17 | 13–24 s |
| `rloo` | `standard_prompt_only` | 2 | 10 prompts + 2 | 8.3 s | 17 | 14–25 s |

GRPO and RLOO generate two completions per prompt and optimize once per two-completion batch. Distillation caps generations at eight new tokens per prompt and scores them with the local teacher. KTO uses five updates for ten rows in the gate and nine for the full split. The full-run ranges include the measured gate, a second launch with checkpoint writing, validation, and training-loop time scaled by the full optimizer step count. The ranges allow for short-process variation. Larger models and datasets need their own estimates.

## Read the results

The launcher writes `experiment/zen/adapters/<task>/<study>/metadata/manifest.json`, the effective settings, and bounded timing and model readback under `reports/`. A successful formal run includes `artifacts/checkpoint.zip`. Normal TRL logs are retained under `logs/`. The optimizer state and the private checkpoint of the gate are disposable and are cleared after validation.

Each stable task has a `training_acceptance` run and a `rejected_inputs` run. The latter uses a missing train split and records that the formal worker did not start. The externally timed acceptance invocations took 17–21 seconds including Python startup, the gate, and the one-step formal phase. The earlier single-step TRL adoption records remain under `experiment/zen/adapters/training/`.

See [additional public workflows](tasks.md) for the Python-only and optional service routes.
