# Compression model families

- **Causal prompt compression** defaults to `NousResearch/Llama-2-7b-hf` through `PromptCompressor()`. It uses language-model token losses to select prompt content. Long-context compression uses the same public compressor with question- and context-sensitive ranking options.
- **LLMLingua-2 token classification** selects words using a Transformers token classifier. The batch default is `microsoft/llmlingua-2-xlm-roberta-large-meetingbank`. The smaller published checkpoint is `microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank`. Choose one with `--model_name` and pin it with `--model_revision`.
- **SecurityLingua token classification** uses the released `SecurityLingua/securitylingua-xlm-s2s` checkpoint with the XLM-RoBERTa tokenizer conventions. The package regression covers tokenizer input preparation for this family.

The model loader builds the tokenizer and selects a causal model or token classifier using Transformers configuration. The [parameter reference](conf.md) shows how to pass device and checkpoint settings.


The [Azure completion adapter](../models/azure_completion/client.py) provides the legacy deployment-based API used by teacher distillation and benchmark generation. The [reproduction guide](../scripts/benchmark_reproduction/README.md) describes its required environment settings.
