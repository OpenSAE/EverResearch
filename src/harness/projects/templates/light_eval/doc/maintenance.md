# Repository layout maintenance

## Purpose and main function

Record the source organization and checks for published language model evaluation paths.

## Scope of application

Use when configuring a model backend, selecting a benchmark or reviewing recorded scores.

## Component layout

`rh projects project check .` initially reported ten issues. The model adapters and benchmark definitions were inside `base/evaluation/`, the top-level dataset and model directories were absent, the top-level task directory contained only the precheck, and three fixture directories exceeded ten direct files. The final check inspected 787 paths and exited successfully with zero violations.

| Area | Change and verification |
| --- | --- |
| Entry points | The CLI dispatcher, Pipeline, and result tracker stay in `base/evaluation/`. Setuptools maps the component roots to the existing Python imports. The editable install and a wheel built from the source distribution opened identical CLI help from the workspace parent and resolved the existing module names. |
| Datasets | Hugging Face loading, optional row filtering, and few-shot split selection moved to `datasets/huggingface_hub/`. PyTorch request batching moved from `base/evaluation/data.py` to `datasets/evaluation_batches/` and retains the `lighteval.data` import. The TruthfulQA precheck loaded its validation data from the bound local cache. |
| Models | Transformers, local engines, endpoints, and test-model adapters moved to `models/adapters/`. Imports continue through `lighteval.models`. Standalone precheck loaded the cached GPT-2 revision `607a30d783dfa663caf39e06633721c8d4cfcd7e` onto CUDA, and Accelerate scored two TruthfulQA validation samples. The Inspect checks used its mock backend. |
| Tasks | The former `base/evaluation/tasks/` subtree moved to `tasks/benchmarks/`, `tasks/core_benchmarks/`, `tasks/multilingual_benchmarks/`, `tasks/language_support/`, and `tasks/prompt_templates/`. Metric code moved to `tasks/metrics/`. The chance baseline computation moved from the CLI to `tasks/chance_baseline/`. Both installations discovered the same 674 core task IDs as before the move. The standalone precheck rejected an unknown task. Pipeline backends and the baseline check prepared samples, and the Inspect command checks the selected datasets before dispatch. |
| Configuration | The result tracker now reads `conf/config.yaml` for existing dataset, model, and task directory names. The result tests cover default study names, explicit output paths, and older response layouts. The wheel includes the same configuration file. |
| Experiments | The independent experiment check passed for the 13 existing executions. The result reader reopened the recorded TruthfulQA inference and replay and matched both stored response rows. A new two-sample inference and replay in a temporary workspace produced matching Parquet rows and score records, with MC1 `1.0` and MC2 `0.916141553913324`. |
| Tests and documents | The 47 metric JSON fixtures are grouped by metric family. Each set of 27 SmolLM2 Parquet fixtures is grouped by benchmark under its existing Transformers or vLLM directory. Both readers discover files recursively. All 705 tests were collected and 73 selected offline tests passed, with three resource-dependent metric cases deselected. The documentation index links to the current component owners. |

The full multilingual registry and the live vLLM, SGLang, and Nanotron paths require optional dependencies absent from the bound environment.

## Previous repository layout maintenance

The source checkout uses `base/evaluation/` for the installed `lighteval` package. The build maps the source directory to the public Python name. The installed console script and imports such as `lighteval.main_accelerate` and `lighteval.tasks.tasks.truthfulqa` were checked through the checkout and a built wheel.

| Area | Checked behavior and result |
| --- | --- |
| Entry points | Installed CLI uses the checkout's experiment directory even when launched from the workspace parent. Explicit fsspec output directories retain their original shape. |
| Datasets | The registry found the TruthfulQA validation split and the precheck prepared a sample using the local dataset cache. |
| Models | Accelerate loaded the pinned GPT-2 revision and completed new CUDA inference. An Inspect AI mock backend covered its local evaluation and log reader. |
| Tasks | Pipeline backends and the chance baseline validate prepared samples before computation. The Inspect path validates selected datasets before dispatch. `lighteval tasks precheck` provides an independent sample check with optional Transformers model construction. |
| Configuration | Backend examples remain explicit YAML inputs. The study catalog records known directory identities, and current runs save effective evaluation settings in `config.json`. |
| Experiments | Eleven earlier runs were reconstructed from their original summaries and details. New inference and replay matched all saved response details and task score fields. The independent experiment check passed for all 13 executions. |
| Tests, docs and examples | Repository test collection found 705 checks. The registry, result reader, baseline and Inspect regression selection ran 36 passing tests with one skipped. Docs source moved intact to `doc/code/evaluation/source/`. The doc-builder workflows now pass the source path explicitly. |

The offline product suite reported 410 passing tests, 29 failures and two skips both before and after the migration. The failures require unavailable cached inputs, remote resources or optional backend support.

## Path changes

- `src/lighteval/` moved to `base/evaluation/`. The build keeps the public distribution and import name `lighteval`.
- `docs/source/` moved to `doc/code/evaluation/source/`. The hosted site's source filenames and navigation remain available to the builder.
- `examples/` moved by use. Backend configurations and runnable examples are under `scripts/examples/`. Task selections are under `assets/examples/task_lists/files/`. Test-only examples and inputs moved to `tests/fixtures/`.
- `tests/unit/` and `tests/slow_tests/` became `tests/product/` and `tests/integration/`. The corresponding tests and consumers now resolve fixture paths under `tests/fixtures/`.
- Prior raw experiment output and acceptance reports are preserved in the original evaluation archive. Current manifests point to individually named score files and response details. [Experiment guide](experiment.md)

## Source names and public imports

EverResearch initially reported 130 violations across 122 source paths. The follow-up layout check passed with 760 checked paths and zero violations. `base/evaluation/module_names.py` maps the affected public module names to the physical source paths. The task registry follows the same mapping and preserves the original discovery order. Benchmark IDs and backend commands continue to identify the same definitions.

| Source group | Current physical location and public access |
| --- | --- |
| CLI settings and shared utilities | `command_arguments.py` supplies `lighteval.cli_args`, and `utilities/` supplies `lighteval.utils`. Metric, model, multilingual, and template helpers remain close to their callers. |
| Model adapters | `models/nanotron_adapter/`, `models/sglang_adapter/`, and `models/vllm_adapter/` supply the corresponding existing Python packages. |
| Core and multilingual benchmarks | Modules stay grouped by purpose or language. For example, the TruthfulQA and GSM8K definitions are in `family_knowledge_qa/truthfulness_questions.py` and `family_math_word_problems/grade_school_math.py`. The public Python modules remain `lighteval.tasks.tasks.truthfulqa` and `lighteval.tasks.tasks.gsm8k`. |
| Instruction and code evaluations | `instruction_following_benchmark/`, `instruction_following_evaluation/`, and `live_code_bench/` hold their respective task entry points and helpers. |
| Prompt templates and metrics | Source files use the names of their operations, such as `question_answering.py` and `standard_error.py`. Callers use the existing public template and metric names. |

The editable checkout and a wheel installed into a separate directory both resolved the old imports and discovered the same 674 core task IDs as the pre-rename checkout. The installed CLI help opened from the workspace parent. The multilingual runtime requires the `lighteval[multilingual]` extra, which was missing in the bound environment.

From the workspace parent, the task precheck loaded the locally cached TruthfulQA validation sample and rejected an unknown task ID. Pytest collected 705 tests. In a paired offline product test run with the same cache configuration, the pre-rename source copy and the current checkout each produced 400 passes, 40 failures and two skips with identical failure IDs. The failures came from unavailable cached models and datasets, remote resources, and optional backend dependencies.

At that stage, the metric and reference-detail fixture directories still exceeded ten direct files. The documentation builder uses the source tree and its navigation file.

The independent experiment checker passed for 13 executions. The result reader located eight saved GPT-2 TruthfulQA response files and loaded matching rows from the original two-example evaluation and its replay. Inspect evaluations retain the native logs for `inspect view`. The available central experiment records cover the studies listed in the experiment guide.

## Verify a copied template

Follow the [environment and resource guide](environment/README.md). Run `python -IS .everresearch/maintain.py check` in the project root. Then use the documented entry point with a small representative input and read back its output. The evidence above describes the reference checks. Measure throughput on the intended model, inputs and hardware before estimating a complete run.
