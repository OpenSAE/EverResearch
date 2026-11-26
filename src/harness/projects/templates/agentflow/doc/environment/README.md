# AgentFlow environment

## Purpose and main function

Set up AgentFlow for inference, benchmarking, or Flow-GRPO training.

## Scope of application

Use this guide when installing the project from a checkout or preparing an experiment.

## Installation

From the project root, run `bash scripts/setup/install.sh` to create the Python 3.11
environment. Activate it with `source .venv/bin/activate`. Use `--dev` to add the
development tools, and use `--training` on a GPU machine configured for the project's
pinned PyTorch, vLLM, and veRL dependencies. Installing the ordinary package leaves the
GPU runtime and Ray services untouched. The benchmark batch scripts also require GNU Parallel.

## Credentials and model servers

Export credentials for the selected providers or create a private `.env` from
[the template](../../base/agent_flow/.env.template). A locally served model requires a
reachable OpenAI-compatible endpoint. Consult [provider setup](../knowledge/workflows/llm_engine.md)
and [local serving](../knowledge/workflows/serve_vllm_local.md) for the available options.

## Verification

After installation, run the following from the project root. The data precheck reads
bundled Bamboogle questions. The training preview displays resolved command arguments.

```bash
agentflow --help
agentflow precheck --data-file assets/prepared_data/benchmark_questions/files/bamboogle/data.json
agentflow train --preview
python -m pytest -q
```

To probe a real model for a benchmark sample, add `--model PROVIDER_MODEL --probe-model` and
provide `--base-url URL` when using a local vLLM server. Flow-GRPO defaults to the
[training YAML](../../conf/config.yaml). Prepare the datasets with the scripts documented
in the [main README](../../README.md) or supply `BASE_DATA_DIR` for an existing dataset root.

Run `agentflow train --precheck` after preparing the training data. The check reads one example
from each local Parquet file selected by the active configuration or command-line overrides.
