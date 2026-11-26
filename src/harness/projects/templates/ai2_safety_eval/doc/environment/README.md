# Ai2SafetyEval environment

## Purpose and main function

Record installation, evaluation resources, and lightweight verification commands.

## Scope of application

Use this page for local installation and for checking the chosen model and task before a larger run.

The upstream dependency list is [requirements.txt](../../requirements.txt). Install it in a dedicated environment along with the project. The full dependency list includes a CUDA-backed vLLM configuration. Local Transformers generation can use an existing compatible PyTorch environment. The keyword refusal classifier runs on a CPU and requires no checkpoint or service credentials.

Set `AI2_SAFETY_EVAL_DATA` to select the location for downloaded benchmark files. Set `HF_HOME` to reuse the machine's Hugging Face cache. API-backed classifiers and judges require credentials for their respective services.

Check command availability with `python -m evaluation.eval --help`. The precheck executes the same task and model on a small subset and returns metric names without writing results.

```bash
safety-eval precheck --mode classification \
  --model_name KeywordBasedRefusalClassifier --task harmbench:response --limit 10
```

The reference Transformers check used a cached Tiny Qwen2.5 checkpoint and the
upstream GSM8K test split. The existing vLLM path requires the full dependencies
and a compatible GPU environment. The XSTest response dataset and WildGuard
tokenizer require access to their gated repositories.

New runs write their selected configurations and results under `experiment/`.
See the [CPU safety evaluation record](../experiment/defensive_evaluation.md) for
available checkpoints, per-task readiness, and runtime estimates.
