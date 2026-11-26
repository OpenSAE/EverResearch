# Additional public TRL workflows

## Purpose and main function

Document the CPU acceptance checks for Python-only trainers and the conditions that block other public modes.

## Scope of application

The training estimates cover the same pinned Zen and tiny Qwen2 fixture workload as the [stable recipes](experiment.md). Treat the upstream example scripts and notebooks as separately configured workloads when they select different data, weights, hardware, or services.

## Python trainer checks

```sh
export PYTHONPATH="$PWD" CUDA_VISIBLE_DEVICES=
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TRL_EXPERIMENTAL_SILENCE=1
timeout -k 3s 295s python scripts/experimental_training.py precheck cpo --report tmp/experimental_acceptance/new_cpo.json
python scripts/experimental_training.py run cpo --report tmp/experimental_acceptance/full_cpo.json
```

Run from the repository root, replace `cpo` with a listed task, and use a fresh report name. A precheck reads ten training units and both official validation rows, trains the real model, and opens a saved tensor. The `run` command repeats that gate before training on all 17 rows and retaining a checkpoint archive. Startup, training, validation and readback time are saved separately. The replay commands write their timed reports under `tmp/experimental_acceptance/`.

| Public trainer route | Script task | Cached Zen configuration | Optimizer steps in gate | Gate time | Estimated one full epoch including the gate |
| --- | --- | --- | ---: | ---: | ---: |
| A2PO | `a2po` | `standard_prompt_only` | 5 | 3.7 s | 6–13 s |
| DPO with BEMA reference updates | `bema` | `standard_preference` | 10 | 4.8 s | 7–15 s |
| CPO | `cpo` | `standard_preference` | 10 | 6.6 s | 10–20 s |
| GKD | `gkd` | `conversational_language_modeling` | 10 | 7.7 s | 13–26 s |
| GMPO | `gmpo` | `standard_prompt_only` | 10 | 4.1 s | 6–14 s |
| GOLD | `gold` | `standard_prompt_completion` | 10 | 5.6 s | 9–18 s |
| IW-OPD | `iwopd` | `conversational_language_modeling` | 10 | 5.1 s | 8–17 s |
| Online DPO | `online_dpo` | `standard_prompt_only` | 10 | 4.4 s | 7–15 s |
| ORPO | `orpo` | `standard_preference` | 10 | 6.3 s | 9–19 s |
| SDFT | `sdft` | `standard_prompt_completion` | 10 | 3.2 s | 5–11 s |
| SDPO | `sdpo` | `standard_prompt_only` | 10 | 4.4 s | 7–15 s |

GKD, GOLD, and IW-OPD use a local teacher loaded from the pinned trainable checkpoint. GMPO and SDPO use the pinned tiny classification reward model, with two completions per prompt. A2PO uses two value samples and the upstream smoke-test parity reward. SDFT uses the real completion field as privileged teacher context. BEMA attaches the reference-model update callback. Each timing includes the existing preprocessing, one CPU process, one library thread, and checkpoint readback. The formal ranges scale only the measured training phase, retain startup and evaluation overhead, and allow for output writing and execution variation.

Online DPO used the pinned tiny Qwen2 classification reward model and generated two completions per prompt, up to eight new tokens each. The check processed ten training prompts and both held-out prompts, reported `eval_loss` of 0.6914, and reopened the saved weights. The measured wall time was 4.4 seconds from launch. The full estimate covers 17 training prompts and two evaluation prompts with batch size one. The run report contains the measured phases.

## Public routes with outstanding runtime evidence

| Route | Observed coverage or blocker | Needed for a full estimate |
| --- | --- | --- |
| `trl vllm-serve` | The command reached the backend and exited because `vllm` is absent in the bound interpreter. | A working vLLM server on a coordinated accelerator, with the selected model and timed generation requests. |
| Stable AsyncGRPO and its experimental import alias | Both import routes resolve. The documented full execution needs a live vLLM rollout server with weight transfer. The bound interpreter has no vLLM. | A rollout server, compatible accelerator allocation, and timed prompt batches that include weight synchronization. |
| Experimental Async Distillation | The Python class imports. The documented path requires reachable teacher HTTP servers and an asynchronous generation backend. No teacher endpoint or vLLM package was available to this CPU run. | A live teacher and rollout path. Multi-teacher mode also requires matching `teacher_id` values and one reachable server per selected teacher. |
| Server Distillation | The class imports. It constructs a teacher client from `teacher_model_server_url`; no teacher service was available. | A configured server that returns tokenizer-aligned teacher log probabilities. |
| IW-OPD teacher-server branch | The local teacher passed. The server branch explicitly requires `teacher_model_server_url`, and no live endpoint was available. | A live teacher serving log probabilities and a probe of the same real batches. |
| GOLD cross-tokenizer and X-Token branches | Local same-tokenizer GOLD passed. Cross-tokenizer and X-Token require different selected teacher/student tokenizers and alignment inputs. | A cached compatible cross-tokenizer pair and the alignment or projection configuration from the example. |
| Harbor and AsyncGRPO/OpenEnv | `harbor` and `openenv` are missing in the bound interpreter. Live task capture and rollout also require the configured environment service and a vLLM backend. | Installed integrations and a task suite with a working capture path. |
| OpenReward | The integration imports lazily. Its runtime `openreward` package is absent and no task service was configured. | An OpenReward endpoint with selected tasks and a repeatable reward request. |
| Model merge callback | `mergekit` is absent. The callback needs two real checkpoints and its configured merge method. | The merge runtime and a representative checkpoint pair. |
| vLLM generation modes of GRPO, RLOO, Online DPO and SDFT | CPU Transformers generation was exercised where supported. vLLM server and colocated modes need the separate vLLM runtime. | Timed backend-specific training and evaluation with a coordinated accelerator. |
| PEFT adapters, bitsandbytes quantization and DeepSpeed | All three packages are absent in the bound interpreter. The CPU runs use full-parameter updates. | The selected optional packages, compatible weights and GPUs, and the proposed adapter or distributed batch layout. |
| Distributed FSDP, multi-GPU and multi-node recipes | Single-process CPU checks cannot exercise synchronization. No multi-accelerator run was allocated. | Actual matching accelerator topology, per-rank batch settings, and checkpoint communication measurements. |
| Multimodal model examples | All measured fixtures are text-only. Model-specific vision, multimodal chat-template, and quantized examples use different weights and selected datasets. | The exact multimodal checkpoints and dataset samples plus the example's runtime. |
| Simulator and browser examples | The bound interpreter lacks `gymnasium`, `browsergym`, and `carla`, and no simulator was configured. | The specific simulator or browser runtime, representative episodes, and generation backend. |
| `trl env` | The installed diagnostic ran. It reports environment versions and does not have a scientific workload. | None. |

The experimental KTO and synchronous distillation aliases resolve to the stable implementations whose real timing is recorded in the stable recipes. The ordinary utilities and trainer configuration APIs are covered by the targeted tests or by the training paths that use them. No GPU job was started for these measurements.
