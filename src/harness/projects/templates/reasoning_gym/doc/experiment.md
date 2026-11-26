# Reasoning Gym runtime profiles

## Purpose and main function

Record what the three research workflows ran, where their results are saved, and how the measured timings scale to a larger run.

## Scope of application

The profiles use procedural chain-sum samples and the same official Qwen2.5 0.5B Instruct checkpoint `Qwen/Qwen2.5-0.5B-Instruct`. The evaluation passes use one completion per prompt and generation capped at 40 tokens. The single-GPU GRPO run uses two completions per prompt with a 24-token cap. The results establish the readiness and cost of these specific settings.

## Measured runs and larger workload estimates

| Run | Measured work and elapsed time | Larger run under the same settings |
| --- | --- | --- |
| Remote API evaluation | 10 prompts, 1 request at a time. CPU service readiness about 5 s, automatic precheck 0.66 s, formal evaluation and writes 6.79 s. 14.75 s end to end including a separate precheck command and service shutdown. | 500 chain-sum prompts, one pass and 500 requests. About 5–8 minutes on the same two-thread CPU service at roughly 0.68 s per prompt. |
| Local evaluation | 10 prompts, batch size 1. Model loading 3.19 s, total precheck including loading and one inference 7.18 s, formal evaluation and writes 39.04 s, 47.53 s end to end. | 500 chain-sum prompts, one pass and 500 completions. About 30–38 minutes using the same two-thread CPU Transformers backend at roughly 3.90 s per prompt. |
| Single-GPU GRPO | 10 train prompts, 10 optimizer steps, 10 validation prompts, one epoch. Two completions per prompt, train and validation completion batch size 2, and one accumulation step. Model load 0.37 s, total automatic precheck 1.31 s, formal training and validation 5.79 s on one RTX 5090 in BF16. 10.26 s end to end. | 20,000 training prompts and 20,000 validation prompts, one epoch, 20,000 optimizer steps, and 80,000 completions. About 2.5–4 hours on the same GPU, including one validation pass and ordinary logging and result writes. Saving a checkpoint adds unmeasured disk I/O and requires additional free storage. |

Each profiling command had a five-minute wall limit including startup and precheck. The CPU runs used two threads on an AMD Ryzen 7 7800X3D. Rates come from the measured small runs and can vary with generation length, sampling settings, and hardware load. The two evaluation prompts differ because the remote run uses a concise arithmetic prompt and the local evaluator uses the library's default prompt. The runs measure the selected workflow, and their scores do not establish model accuracy. The GRPO run exercised optimizer updates and validation. Some batches produced identical rewards within a group and therefore zero policy gradients. It kept metrics and progress, with model checkpoint saving disabled.

## Reproduce or scale a run

Install the relevant environment listed in the [environment guide](environment/README.md). Use a new descriptive `--study` for each new run. The commands below use the smaller [profile recipes](../assets/recipes/workflow_profiles/README.md). For a full evaluation, copy the selected recipe and change the chain-sum dataset's `size` to `500`. For a full training pass, change `dataset_size` to `20000` and leave the single epoch and epoch-end validation unchanged.

1. Remote evaluation. Start the OpenAI-compatible server with the official local checkpoint, then use the HTTP evaluator.

   ```sh
   OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 transformers serve \
     Qwen/Qwen2.5-0.5B-Instruct --device cpu --dtype float32 \
     --host 127.0.0.1 --port 17843 --default-seed 43
   python main.py evaluate --config assets/recipes/workflow_profiles/files/remote_evaluation.yaml \
     --base-url http://127.0.0.1:17843/v1 --api-key local --timeout 12 \
     --full-results --study arithmetic_endpoint_study
   ```

2. Local evaluation. Use the Transformers recipe and the same two-thread CPU configuration.

   ```sh
   OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 python main.py evaluate-local \
     --config assets/recipes/workflow_profiles/files/local_evaluation.yaml \
     --device cpu --study arithmetic_response_study
   ```

3. Training. Use the PyTorch, Transformers, and TRL environment that provides `GRPOTrainer`, with a CUDA device available. The profile ran with the TRL version found in the accompanying [TRL template](https://github.com/OpenSAE/EverResearch/tree/main/src/harness/projects/templates/trl).

   ```sh
   python main.py train-single --config assets/recipes/workflow_profiles/files/policy_training.yaml \
     --study arithmetic_policy_study
   ```

Use `--precheck` on any of these commands for a bounded check without starting a formal run. The remote command also offers `--datasets-only` without contacting the endpoint. The successful evaluation and training records and their corresponding rejected inputs passed the central precheck validation. Use `python main.py read-run <directory>` for the current records or the original flat result directories. Remote evaluation also accepts `--resume <directory>` for existing checkpoints.

The timed reference runs used cached weights. Cache the official checkpoint before measuring the same workload. The hosted OpenRouter deployment, vLLM backend, and the paper's distributed veRL recipe still require their corresponding service or frameworks for a runtime measurement. The local Transformers, local HTTP service, and single-GPU TRL timings apply to the options above.
