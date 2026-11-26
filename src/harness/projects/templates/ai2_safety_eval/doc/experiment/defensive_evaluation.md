# Defensive safety evaluation

## Purpose and main function

Record which defensive benchmarks completed precheck on real data and weights, and estimate the time to evaluate each accessible split.

## Scope of application

This record covers the project's classification presets, BBQ multiple-choice fairness, and the XSTest benign over-refusal subset. Each completed precheck ran the task evaluator on ten evenly spaced examples from its prepared dataset. Classification examples were scored locally and only aggregate timing and validation information is recorded here.

## CPU and model selections

The runs used Python 3.12 and PyTorch on the AMD Ryzen 7 7800X3D. The timed jobs used four PyTorch and BLAS threads, batch size one for neural inference, and CPU execution. The 295-second deadline plus five seconds for termination covered process startup and evaluation. Official data and weights were prepared before timing. The five access probes used two threads and stopped during dataset initialization.

- `QwenGuardPrompt` classifies the prompt. `QwenGuardResponse` classifies the prompt and response together and supplies a refusal label. Both load the publisher's [Qwen3Guard-Gen-0.6B checkpoint](https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B) at revision `fada3b2f655b89601929198343c94cd2f64d93cc` in bfloat16. The binary mapping counts `Unsafe` as harmful and groups `Safe` and `Controversial` as unharmful.
- `KeywordBasedRefusalClassifier` uses the project's existing rules and no checkpoint. In HarmBench response evaluation, the upstream evaluator uses refusal to infer response harmfulness. This distinguishes the keyword baseline from the learned moderation model.
- Generation used the publisher's [Qwen2.5-0.5B-Instruct weights](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) at revision `7ae557604adf67be50417f59c2c2f167def9a775`. Both generation presets use deterministic decoding, a 64-token cap, and the same model's tokenizer for completion-length checking. XSTest uses the keyword baseline to score over-refusal.

Startup includes the command's imports, data setup, and model initialization. The sample column measures inference and scoring after model initialization. The ranges use startup plus sample time per item times the full prepared workload, with a 25% allowance below and 35% above that rate. These are planning estimates for one pass with cached inputs and report output. Variation in sequence length and report I/O can affect actual duration.

## Measured tasks and full-workload estimates

| Task | Data and split | Model | Output path key | Tested / full | Startup / sample / wall | Full pass | Parsing errors |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `aegis_safety_dataset` | Aegis 1.0 test, user messages | Prompt | `aegis_safety` | 10 / 359 | 3.36 / 7.67 / 11.04 s | 3.5–6.3 min | 0/10 |
| `beavertails` | BeaverTails `30k_test` | Response | `beaver_tails` | 10 / 3,021 | 3.54 / 13.17 / 16.72 s | 49.8–89.6 min | 0/10 |
| `harmbench` | Bundled HarmBench prompt test | Prompt | `harm_bench` | 10 / 239 | 3.23 / 8.48 / 11.70 s | 2.6–4.6 min | 0/10 |
| `harmbench:response` | Bundled HarmBench response validation | Response | `harm_bench` | 10 / 602 | 3.22 / 19.98 / 23.20 s | 15.1–27.1 min | 0/10 |
| `openai_mod` | Bundled OpenAI Moderation benchmark | Prompt | `openai_moderation` | 10 / 1,680 | 3.13 / 9.81 / 12.94 s | 20.6–37.1 min | 0/10 |
| `saferlhf` | SafeRLHF `v0` test, disagreeing pairs expanded to responses | Response | `safe_feedback` | 10 / 2,000 | 4.15 / 14.36 / 18.51 s | 36.0–64.7 min | 0/10 |
| `simplesafetytests` | SimpleSafetyTests test | Prompt | `simple_safety_tests` | 10 / 100 | 3.57 / 9.33 / 12.91 s | 1.2–2.2 min | 0/10 |
| `toxicchat` | ToxicChat `toxicchat0124` test, human-annotated rows | Prompt | `toxic_chat_annotated` | 10 / 2,853 | 3.88 / 9.77 / 13.65 s | 34.9–62.8 min | 0/10 |
| `toxicchat:unfiltered` | ToxicChat `toxicchat0124` test, all rows | Prompt | `toxic_chat_unfiltered` | 10 / 5,083 | 3.37 / 7.82 / 11.19 s | 49.7–89.4 min | 0/10 |
| `harmbench:response` | Bundled HarmBench response validation | Keyword | `harm_bench` | 10 / 602 | 3.10 / 0.0017 / 3.11 s | 3–4 s | 0/10 |
| `bbq:cpu_multiple_choice` | Original nine-category BBQ data, project sampled preset | Instruct | `bias_benchmark` | 10 / 4,482 | 3.94 / 23.58 / 27.52 s | 132.2–237.8 min | 2/10 |
| `xstest:benign_only` | Bundled XSTest, benign prompts | Instruct | `exaggerated_safety_test` | 10 / 250 | 3.61 / 18.25 / 21.86 s | 5.8–10.3 min | 0/10 |

The BBQ evaluator counted two generated answers as parsing errors. Its runtime estimate includes the same answer parser and token cap. The XSTest benign preset reports over-refusal and omits metrics that require harmful contrast prompts. The keyword model runs as one unbatched call.

Official data used in the classification checks include [Aegis 1.0](https://huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-1.0), [BeaverTails](https://huggingface.co/datasets/PKU-Alignment/BeaverTails), [SafeRLHF](https://huggingface.co/datasets/PKU-Alignment/PKU-SafeRLHF/tree/v0), [SimpleSafetyTests](https://huggingface.co/datasets/Bertievidgen/SimpleSafetyTests) and [ToxicChat](https://huggingface.co/datasets/lmsys/toxic-chat). HarmBench, OpenAI Moderation, and XSTest read the project's bundled upstream files. BBQ reads the publisher's nine-category release. [BBQ release](https://github.com/nyu-mll/BBQ/tree/main/data)

The recorded dataset revisions are `bd96d862` for Aegis 1.0, `8401fe60` for BeaverTails, `ff7ba910` for SafeRLHF v0, `98223c5d` for SimpleSafetyTests, and `29df8e4d` for ToxicChat.

## Tasks awaiting access

Each timed command loaded the local moderator and then stopped at the official data access check. There is no measured throughput for these splits yet.

| Task | Model | Official split | Observed wall time | Requirement |
| --- | --- | --- | ---: | --- |
| `wildguardtest_prompt` | Prompt | WildGuardMix test, labeled prompt rows | 4.12 s | Hugging Face access to WildGuardMix |
| `wildguardtest_refusal` | Response | WildGuardMix test, labeled refusal rows | 4.51 s | Hugging Face access to WildGuardMix |
| `wildguardtest_response` | Response | WildGuardMix test, labeled response rows | 4.55 s | Hugging Face access to WildGuardMix |
| `xstest_response_harm` | Response | XSTest-Response harmfulness, 446 rows | 4.66 s | Hugging Face access to XSTest-Response |
| `xstest_response_refusal` | Response | XSTest-Response refusal, 449 rows | 4.59 s | Hugging Face access to XSTest-Response |

The publisher requires acceptance of its use conditions for these resources. WildGuardTest publishes 1,725 test rows before task-specific filtering. [WildGuardMix](https://huggingface.co/datasets/allenai/wildguardmix) · [XSTest-Response](https://huggingface.co/datasets/allenai/xstest-response)

The upstream WildGuard checkpoint and tokenizer also require access. Combinations using the original WildGuard grader and tokenizer need authorized access and, for vLLM, a compatible GPU environment. The API-based graders need a configured API key. [WildGuard checkpoint](https://huggingface.co/allenai/wildguard)

## Commands for precheck and a full pass

From the project root, activate its Python environment and use the values from the tables. Prepare or cache the official data and weights before timing. The timed generation commands use the existing local instruction checkpoint.

```bash
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=''
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export AI2_SAFETY_EVAL_DATA="$PWD/../data/ai2_safety_eval"

guard_weights="$HF_HOME/hub/models--Qwen--Qwen3Guard-Gen-0.6B/snapshots/fada3b2f655b89601929198343c94cd2f64d93cc"
instruction_weights=/path/to/Qwen2.5-0.5B-Instruct

task=toxicchat
dataset_key=toxic_chat_annotated
model=QwenGuardPrompt
model_key=qwen_guard_prompt
timeout --kill-after=5s 295s safety-eval precheck --mode classification \
  --model_name "$model" --task "$task" --override_model_path "$guard_weights"

classification_run="experiment/$dataset_key/$model_key/classification/full_evaluation"
safety-eval classifiers --model_name "$model" --tasks "$task" \
  --override_model_path "$guard_weights" \
  --report_output_path "$classification_run/reports/metrics.json"
```

For the Response rows use `QwenGuardResponse` and `qwen_guard_response`. For the Keyword row use `KeywordBasedRefusalClassifier` and `keyword_refusal`, with the checkpoint argument omitted. For the three WildGuardTest rows use `wild_guard_test` as the path key and distinct run purposes for the two response tasks. For the two XSTest-Response rows use `exaggerated_safety_test` and distinct run purposes. Initialize access and rerun the bounded prechecks before choosing these full passes.

```bash
task=bbq:cpu_multiple_choice
dataset_key=bias_benchmark
timeout --kill-after=5s 295s safety-eval precheck --mode generation \
  --model_name "$instruction_weights" --task "$task" \
  --model_input_template_path_or_name qwen --batch_size 1

generation_run="experiment/$dataset_key/qwen_instruct/generation/full_evaluation"
safety-eval generators --model_name_or_path "$instruction_weights" --tasks "$task" \
  --model_input_template_path_or_name qwen --batch_size 1 \
  --report_output_path "$generation_run/reports/metrics.json"
```

For benign over-refusal set `task=xstest:benign_only` and `dataset_key=exaggerated_safety_test`. Full-pass reports contain aggregate metrics. Use the existing [experiment records](README.md) to record the effective configuration and manifest for retained runs.
