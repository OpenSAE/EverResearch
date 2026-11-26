# FlagEmbedding environment

## Purpose

This page describes how to install FlagEmbedding, prepare devices and inputs, and check which environment the package and evaluation commands use.

## Scope

Use this page when setting up a checkout for inference, evaluation, or fine-tuning. Each historical result carries its own execution conditions. Use the reports linked from the [experiment index](../experiment.md) when reproducing those results.

## Installation

From the checkout root, create and activate a Python virtual environment. Python 3.11 is the version verified below. The project's dependency ranges and optional extras are declared in [setup.py](../../setup.py).

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For retrieval evaluation, install the evaluation extra to add CPU FAISS and `pytrec_eval`. BEIR also needs `beir`, MTEB uses `mteb==1.15.0`, and AIR-Bench needs `air-benchmark`. Install the backend for the benchmark you plan to run. For GPU FAISS, use a build compatible with your CUDA environment in place of CPU FAISS. The fine-tuning extra declares DeepSpeed and FlashAttention. Prepare these dependencies against the intended PyTorch, CUDA, and compiler versions when the selected recipe uses them. The [evaluation recipes](../../scripts/examples/evaluation/README.md) list benchmark-specific dependencies and arguments.

```bash
python -m pip install -e '.[evaluation]' beir pytest
```

## Devices and inputs

For evaluation, pass `--devices cpu` for CPU inference or `--devices cuda:0` for the first visible CUDA GPU. Select enough device memory for the chosen model, precision, sequence length, and batch size. The generated checkpoints used by the retrieval tests run on CPU.

Pass a local model directory or a Hugging Face model identifier to `--embedder_name_or_path` and, when reranking, `--reranker_name_or_path`. Local model inference requires the configuration, tokenizer, and checkpoint weights. For a local Custom evaluation, point `--dataset_dir` to a directory containing `corpus.jsonl`, `test_queries.jsonl`, and `test_qrels.jsonl` for the test split. With the BEIR command, put those files under a dataset directory such as `fiqa/` and pass its parent as the dataset root. Use the [evaluation parameter guide](../conf.md) to choose output paths, caches, and settings for the selected command.

## Lightweight checks

From the checkout root with the selected environment active, check the active interpreter, package source, and device, then open the Custom evaluation help. The retrieval tests under `tests/` generate local inputs and checkpoints. Setting both offline environment variables keeps these checks local.

```bash
python -c 'import sys, torch, FlagEmbedding; print(sys.executable); print(FlagEmbedding.__file__); print(torch.__version__, torch.version.cuda, torch.cuda.is_available())'
python -m FlagEmbedding.evaluation.custom --help
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 python -m pytest -q tests/test_retrieval_evaluation.py
```

See the [test guide](../../tests/README.md) for the wider suite and its published-checkpoint requirements.

## Environment verified on November 20, 2026

The reference installation used Python 3.11.17, FlagEmbedding 1.4.2 imported from the editable checkout, PyTorch 2.15.0 with CUDA 13.2, and Transformers 4.57.6. PyTorch detected one NVIDIA GeForce RTX 5090 with 31.4 GiB of memory. CPU FAISS, `pytrec_eval`, and BEIR were installed. MTEB, AIR-Bench, DeepSpeed, and FlashAttention require separate installation in this environment.

For a new run, place FiQA inputs and BGE weights in user-selected data and model directories. The three reference BGE directories contain local configurations and tokenizers. A fresh run with those directories also requires the corresponding weights. Historical FiQA conditions are recorded in the [similarity archive](../../assets/history_experiment/fiqa_similarity/README.md) and [retrieval archive](../../assets/history_experiment/fiqa_retrieval/README.md).
