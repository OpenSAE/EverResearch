# Project maintenance record

## Purpose and main function

Map compression, evaluation and training entry points and document their verified behavior.

## Scope of application

Use when preparing prompts, benchmark data or model weights and reading the run outputs.

This record covers the LLMLingua checkout at baseline commit `01b9e94`, including the installable API, the benchmark and training workflows, documentation, and local software verification.

| Area | Entry point, findings and disposition |
| --- | --- |
| Runtime | `make install` previously looked for a wheel with a different distribution name. It now installs this checkout through pip. The managed `python -m llmlingua compress` command and the original `evaluation/compress.py` share argument definitions and compression dispatch. Preview resolves input and experiment paths and prints effective settings before the input is opened. Verified the wheel build, CLI preview and standalone compatibility. |
| Datasets | Batch JSON preserves sample indices, prompts and reference fields through evaluation input. MeetingBank's source formatter maps its training transcripts and summaries to this format. The labeler accepts both locally generated indexed JSON and a Hugging Face dataset. The LLMLingua-2 recipes link annotation output to filtering and training. Training uses a shuffled chunk-level 80/20 division and its validation scores select the checkpoint. Meeting-level separation would require provenance retained through filtering and a different split. |
| Models | The main API selects a Transformers causal language model or token classifier from model architecture. The LLMLingua-2 benchmark defaults to the XLM-RoBERTa MeetingBank classifier. The loader copies configuration before consuming local options and preserves padding token ID zero. Token classifier input conventions and word-boundary detection now share the same family lookup, including the published SecurityLingua model name. The shared spaCy training adapter remains separate from inference because it expands word labels into subword targets. |
| Tasks | Batch compression retains the original sample-indexed output format used by downstream evaluators. The original script keeps incremental writes and continuation by sample ID. The six benchmark-specific evaluators retain their distinct downstream prompts and metrics. For GSM8K, the evaluator now accepts the test question file explicitly and reads the 250-token demonstration output produced by its matching shell recipe. |
| Configuration | The API and original evaluation script keep their constructor and compression defaults. The managed entry records the effective command settings in `config.json`. The [argument reference](conf.md) documents the public settings and path resolution. Checks exercised default values, overrides, output-name validation, forced tokens and model option preservation. |
| Experiments | Managed results are created under a dataset and model identity with a named purpose, a unique invocation directory, a configuration, a manifest and the indexed result. The standalone benchmark and training recipes use the fixed checkout `experiment/` root by default and retain explicit paths for historical output. The shell dry checks matched every compression output to its evaluation input and the annotation output to the training input. At the baseline, the checkout contained reproduction source but no local result directories or result files to migrate. |
| Scripts, tests and docs | The Python API, notebook examples and documented reproduction script locations remain usable. The three checkpoint-backed test classes now perform setup during execution, so test collection is offline. The standalone [project guide](README.md) maps the source, runtime, datasets, models, tasks and outputs. |

The recursive inventory found one directory above ten directly maintained files, the checkout root. Its 14 files consist of build and configuration entry points, the published API guide, GitHub-facing repository documents and local agent instructions. These paths have distinct roles and are retained for build discovery, published links and repository metadata. The largest research directories have nine direct source, configuration or documentation files each. The `.git/` database, synchronized skill links and interpreter caches are inventoried by their owning tool or project convention.

## Structure and software verification

- Repository-root pytest discovered 15 cases, including five checkpoint-backed cases. The 10 offline cases passed.
- The normal managed command loaded a locally generated, one-layer BERT token classifier on CPU and compressed `the team met today to plan a show` to `team today plan` in the observed run. The reader recovered sample `17`, its unchanged reference and the selected local checkpoint. The byte tokenizer used for the token-count estimate and the randomly initialized model were synthetic.
- Wheel installation into a temporary directory exercised the packaged command and preserved the Python import. Bash syntax checks and intercepted command arguments checked recipe paths without invoking external services.
- The legacy SecurityLingua trainer saves a PyTorch state dictionary. The released Transformers checkpoints follow the package's normal loading interface.

## Real model and dataset verification

Both local compression paths ran on the RTX 5090 with Python 3.12.15, PyTorch 2.11.0+cu128, Transformers 4.57.6, Accelerate 1.15.0, and tiktoken 0.14.0. The EverResearch `llmlingua` binding uses the reference Python environment and the project-specific cache under `/workspace/data/llmlingua/hub`. This interpreter uses the host's PyTorch stack with a project-local editable package install.

| Area | Evidence from the real runs |
| --- | --- |
| Runtime | The public `PromptCompressor` API ran the first upstream Quick Start. `python -m llmlingua compress` ran the batch workflow and `python -m llmlingua show` read back both manifests, configurations and artifacts. |
| Datasets | The Quick Start uses the GSM8K demonstrations linked in the upstream CoT notebook, pinned to `461e2d551f3f12d54caee75fa1e915fdbc3e9d12`. The record links the notebook's GSM8K test row 2 as its reference question, sourced from `openai/grade-school-math` at `3101c7d5072418e28b9008a6636bde82a006892c`. Compression operates on the demonstrations. The batch input carries the first three `huuuyeah/meetingbank` test records from `5b4fb6f67f490be93e249d70b732780932d19fe3`, with original transcripts, summaries and segment identifiers. |
| Models | The Quick Start uses the API default `NousResearch/Llama-2-7b-hf` at `8efe6c9b93655b934e27bd9981e3ec13e55aee9d`. The batch uses its default `microsoft/llmlingua-2-xlm-roberta-large-meetingbank` at `ebaba9b0e874dadd3003ffcff828e4397e568089`. Both ran locally from cached safetensors. |
| Tasks | The Quick Start's 200-token target yielded 2,365 → 209 tokens, or 11.3× by independent token counting. The batch compressed its three transcripts from 1,341 → 619, 626 → 300 and 316 → 137 tokens. The reader preserved every input row and reference field. These measurements cover compression and output integrity. Downstream answer quality and paper benchmark scores remain separate evaluations. |
| Configuration | The API passes a revision through `model_config`. The batch command now accepts `--model_revision`, forwards it to the same loader, and saves it in effective settings. `--show-config` confirmed the MeetingBank input, default classifier and 0.5 rate before inference. |
| Experiments | Both LLMLingua-2 variants use `llmlingua_2/<variant>` for new managed runs. Run identity, selected model and effective options remain in the run records. The regression exercised both variant paths and read a result from the earlier provider-based layout. |
| Scripts, tests and docs | Ten local cases passed in `tests/test_batch_compression.py`. The saved result directories include run logs and reproducible checks. The first Quick Start attempt ran inference and stopped in the verification wrapper, which initially counted trailing whitespace. The completed run uses the public API's documented text normalization and has a separate manifest. |

Successful local result directories, relative to the checkout:

- `experiment/gsm8k/nousresearch_llama_2_7b_hf/compression/readme_quick_start/20261120T110839.354122Z-59f530d0/`
- `experiment/meetingbank/llmlingua_2/xlm_roberta_large_meetingbank/compression/transcript_compression/20261120T110724.590761Z-018d6c86/`

Each result directory includes `metadata/reproduction.md` with the actual commands, input source and readback entry. The three MeetingBank rows are raw test transcripts. The separate MeetingBank Short QA recipe uses preformatted questions and a downstream answer model.

## Directory and experiment migration

The migration preserved installed imports and entry points after moving the source by responsibility.

| Previous location | Disposition and verification |
| --- | --- |
| `llmlingua/` | The build maps the public `llmlingua` package to `base/prompt_compression/`. The published package, module command and `llmlingua.utils` import remain usable in editable and wheel installations. |
| `examples/`, `images/` | The seven notebooks moved to `scripts/examples/` under descriptive names. The original illustrations moved to `assets/illustrations/prompt_compression/files/`. The quick start links to their current paths. |
| `experiments/llmlingua2/` | Collection, training and benchmark evaluation moved to `scripts/benchmark_reproduction/`. Benchmark-specific scoring remains separate. Its six evaluator filenames now describe the corresponding benchmarks or tasks. The shell recipes point to the new script locations. |
| `experiments/securitylingua/` | The existing SecurityLingua reproduction sources moved to `scripts/security_training/`, with the guide linked from the root README. |
| Root policy documents and `DOCUMENT.md` | The API guide moved to `doc/code/interface.md`. Transparency, conduct, security and support material moved to `doc/knowledge/`. The root README links to these documents. |
| Three model-backed test files | The filenames describe prompt, classifier and long-context compression. Root test discovery includes all three. |
| `experiment/gsm8k/` and `experiment/meetingbank/` | The two successful runs and one failed attempt moved under canonical dataset, checkpoint and purpose names, with execution IDs stored under `executions/`. Original configurations, output files and logs are retained. Earlier manifests and reproduction text remain alongside the current records. |

| Area | Review outcome |
| --- | --- |
| Runtime | The bound interpreter uses the package from the new physical checkout. An independently installed wheel exposes the same import and command. Configuration preview prints effective input, model options and canonical component paths before opening inputs. |
| Datasets | The existing indexed reader and training loaders keep their input contracts. Readback confirmed that MeetingBank's three output rows retain their original identities and fields. Grade School Math retains its source prompts and the pinned reference question in the run record. |
| Models | The causal model and both LLMLingua-2 classifier checkpoint identities are registered for experiment paths. The offline regression checks padding ID zero and that model loader settings are retained. The existing real outputs show the causal and large classifier paths. |
| Tasks | The managed batch command and the standalone benchmark compressor execute the first eligible sample as a precheck and reuse it. The managed command persists the checked sample ID and exposes a precheck-only mode. The offline suite covers precheck-only, repeated execution, unsuccessful model construction, and standalone resume. The benchmark evaluators, corpus preparation and trainers still use their own entry points. |
| Configuration | The existing model and compression defaults are retained. The new `--precheck` mode and the mapping of canonical paths are described in the [parameter reference](conf.md). |
| Experiments | Central layout and experiment checks passed. The project reader opened all three existing runs from both their current and previously published paths. The active run locations and coverage are indexed in the [experiment guide](experiment.md). The older shell recipes continue using direct filenames for handoff. |
| Scripts, tests and docs | All shell scripts passed syntax checking. Repository test discovery found 15 cases and 10 offline cases ran successfully. Validation used saved outputs for real model and data evidence. |

The direct benchmark, collection and training recipes retain historical output destinations and execution conventions. Full end-to-end acceptance of those paths requires dataset and service-specific runs and integration with the managed precheck and result contract.

## Component layout and managed runtime verification

| Area | Changes and evidence |
| --- | --- |
| Runtime | `base/prompt_compression/` exposes the package API and command and dispatches to the root-level components. Both the editable install and the wheel preserve `llmlingua.PromptCompressor`, `llmlingua.prompt_compressor` and `llmlingua.utils`. The wheel requires an explicit result root when started outside an LLMLingua checkout. Configuration preview remains available there. |
| Datasets | `datasets/indexed_prompts/` reads batch JSON. `datasets/token_classification/` prepares inference tensors, and `datasets/classifier_training/` prepares labeled classifier inputs. The offline checks cover indexed JSON selection, resume and preservation of references. The earlier MeetingBank run still exposes its three original records. |
| Models | `models/transformer_compression/` loads Hugging Face causal models and token classifiers. A local BERT tokenizer determines its word-boundary rules even when its checkpoint directory has a custom name. A randomly initialized one-layer BERT checkpoint ran the CPU smoke test. The published causal and XLM-RoBERTa checkpoints remain represented by the existing runs. |
| Tasks | `tasks/compression/` owns the compression algorithms and batch operation. The managed command and legacy benchmark compressor reuse their first sample. The managed run records one prechecked sample, elapsed time and formal-start state. The central precheck command accepted a successful two-row synthetic run and a failure with an absent checkpoint. The public API, paper label collection, trainers and downstream evaluators have separate execution conventions. |
| Configuration | `conf/config.yaml` supplies the default batch checkpoint and maps registered dataset and checkpoint identities to result paths. The parser accepts explicit checkpoint overrides. Preview exercised the yaml bundled in the wheel, the editable checkout and custom path values. |
| Experiments | The three pre-existing records remain readable through `python -m llmlingua show`. They contain two completed runs and one failed attempt. The synthetic readback confirmed sample IDs and reference preservation. |
| Scripts, tests and docs | All shell recipes passed syntax checking. The standalone benchmark compressor displayed help from the relocated installation. All 11 offline tests passed and pytest collected 16 cases. The layout guide, configuration reference and task notes describe the current paths. The end-to-end training, paper evaluation and five model-backed test cases remain outside this offline verification. |

The final central project check examined 180 paths with no violations. The independent experiment check accepted all three existing runs. The synthetic precheck took 0.34 seconds on CPU and checked one sample. The temporary synthetic runs and wheel installation were removed after verification.

## Paper and SecurityLingua workflow implementation layout

The benchmark and SecurityLingua command paths remain available through their original script launchers. The implementations now install with the project and occupy the same component directories as the managed compression workflow.

| Area | Changes and evidence |
| --- | --- |
| Runtime | `setup.py` maps the annotation, Azure completion, distillation, classifier training and benchmark evaluation packages into the existing `llmlingua` namespace. Verified editable installation and independently installed wheel imports, including the existing public compressor. |
| Datasets | `datasets/prompt_annotation/` handles MeetingBank transcript formatting, label alignment, filtering and SecurityLingua pairs. Both trainers use the same `datasets/classifier_training/` loader and tokenization contract. The 80/20 MeetingBank split and 90/10 SecurityLingua split retain their historical chunk-level divisions. A local teacher output and the labeler reproduced retained-token targets for the same input row. |
| Models | `models/azure_completion/` holds the shared Azure completion adapter and distillation teacher. `models/transformer_compression/` supplies the common two-class checkpoint constructor for both trainers. A one-layer CPU BERT training run wrote a Transformers checkpoint that could be reloaded, along with the historical PyTorch state dictionary. |
| Tasks | `tasks/distillation/` owns teacher compression, `tasks/classifier_training/` owns both trainers, and `tasks/benchmark_evaluation/` owns all six downstream evaluators and their shared metrics. Evaluators and teacher compression check input fields. Both trainers use the shared labeled-sample precheck. Grade School Math wrote readable predictions and scores using a local completion stub. LongBench rejected missing fields before creating results. The MeetingBank trainer rejected misaligned labels before creating model or log files. The managed and standalone batch compressors continue to reuse the checked first result. |
| Configuration | The managed batch defaults remain in `conf/config.yaml`. The teacher instructions live under `conf/tasks/distillation/` and are bundled in the wheel. The Azure adapter reads deployment credentials from its environment. The BBH reasoning launcher accepts an explicit question-file path through `--load_data_from`. |
| Experiments | The normal reader reopened two completed compression runs and one failed attempt, with output counts of one, three and zero. The reproduction launchers retain their explicit file destinations for handoff. Their current outputs still use those file-level contracts. Managed run manifests and precheck records currently cover the package batch command. |
| Scripts, tests and docs | All 15 Python reproduction launchers displayed help. Bash syntax checks passed. Pytest collected 16 cases and the 11 offline tests passed. The reproduction guides identify each implementation and the dependencies used by its existing command. |

The final central project check covered 204 paths with exit status `0` and an empty violation list. The independent experiment check accepted the three saved runs. The local reproduction checks used synthetic inputs, a one-layer checkpoint, a deterministic Azure completion stub and a whitespace tokenizer in place of the spaCy model. Full paper scoring, real corpus preparation, SecurityLingua training, and checkpoint-backed regression cases still require their own datasets, models and runtime dependencies. ZERO-SCROLLS also uses a separately distributed benchmark metric. The source migration and saved-result checks required no new real research run.

## Verify a copied template

Follow the [environment and resource guide](environment/README.md). Run `python -IS .everresearch/maintain.py check` in the project root. Then use the documented entry point with a small representative input and read back its output. The evidence above describes the reference checks. Measure throughput on the intended model, inputs and hardware before estimating a complete run.
