# Evaluation data

## Purpose and main functions

`datasets/huggingface_hub/` loads benchmark data with the selected Hub repository, subset, revision, and input files. It applies task-specified row filters and resolves candidate few-shot splits. `datasets/evaluation_batches/` groups formatted requests by length for model adapters and restores the original order after inference.

## Scope

Use this page to locate a benchmark's input or change the shared sample-loading code. The task selection determines the dataset; custom tasks declare their input with the same `LightevalTaskConfig` fields. The public `lighteval.data` import provides the PyTorch batching classes.

## Shared parameters

Task definitions supply `hf_repo`, `hf_subset`, `evaluation_splits`, and any optional revision, files, or filters. Evaluation and few-shot formatting are attached to each task. Backend limits and study configuration are described in the configuration guide. [Evaluation inputs and configuration](conf.md)

## Datasets

### `truthfulqa/truthful_qa`

`truthfulqa:mc` uses the `multiple_choice` subset and the validation split. The task constructs answer choices and target indices for evaluation or a guessing baseline. Use `lighteval tasks precheck truthfulqa:mc` to check the prepared sample with a local cache. [TruthfulQA definition](../tasks/core_benchmarks/family_knowledge_qa/truthfulness_questions.py)

### `openai/gsm8k`

`gsm8k` reads the `main` subset and uses the test split for grade-school word problems. The task prepares question prompts and extracts the expected answer from each record. [GSM8K definition](../tasks/core_benchmarks/family_math_word_problems/grade_school_math.py)

### `Idavidrein/gpqa`

`gpqa:diamond` uses the `gpqa_diamond` subset and the declared `train` split. The task builds a question with four answer choices and a target for Inspect AI. Hub access depends on the dataset permissions of the running account. [GPQA definition](../tasks/core_benchmarks/family_knowledge_qa/graduate_science.py)
