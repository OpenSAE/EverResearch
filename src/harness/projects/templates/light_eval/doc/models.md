# Model adapters

## Purpose and main functions

`models/adapters/` supplies backend configurations, model construction, and evaluation responses from local checkpoints or inference services.

## Scope

Use this page when choosing a backend or following a Pipeline request through a model adapter. The installed package exports these interfaces under `lighteval.models`.

## Shared parameters

The Pipeline selects an adapter from its model configuration. Local backends accept model IDs and applicable loader parameters such as the revision, batch size, or generation settings. Example YAML configurations and the command-line override format are described in the configuration guide. [Evaluation inputs and configuration](conf.md)

## Model backends

- **Transformers and Accelerate** load local or Hub checkpoints. The Quick Tour uses GPT-2 for multiple-choice scoring, and the README demonstrates a Llama checkpoint for generation. Each configuration identifies the model and any optional tokenizer, revision, and runtime settings. [Transformers adapter](../models/adapters/transformers/transformers_model.py)
- **vLLM, SGLang, and Nanotron** provide local engines with their own optional dependencies and parallelism settings. The repository's backend examples give the settings for each engine. [Backend example configurations](../scripts/examples/model_configs/)
- **Endpoint adapters** call TGI, inference endpoints, inference providers, or LiteLLM. They supply credentials and endpoint settings through the selected backend's normal configuration. With `lighteval eval`, Inspect AI loads its own model by provider and name. [Model adapter source](../models/adapters/endpoints/)
