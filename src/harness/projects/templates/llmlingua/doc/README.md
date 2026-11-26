# LLMLingua project structure

[Execution environment](environment/README.md) covers installation, resources, and how to check which environment a run used.

The [quick start](../README.md) is the entry point for library users. The [API guide](code/interface.md) covers compression, structured input and retrieval integrations. The [LLMLingua-2 paper workflows](../scripts/benchmark_reproduction/README.md) cover data preparation, classifier training and downstream evaluation.

See the [datasets](datasets.md), [models](models.md), [tasks](tasks.md) and [experiment records](experiment.md) for component choices and results.

## Working directories

| Path | Purpose and callers |
| --- | --- |
| `base/prompt_compression/` | Public Python imports and module command. The package exposes `PromptCompressor` to external callers and notebooks. |
| `models/transformer_compression/` | Transformers model and tokenizer construction shared by compression and classifier training. |
| `datasets/` | Indexed JSON prompt loading, inference tensor preparation and preparation of word-labeled training examples, and MeetingBank and SecurityLingua annotation and filtering. Training preprocessing loads the spaCy English model when a training dataset is constructed. |
| `tasks/compression/` | The public compression algorithms and the LLMLingua-2 batch operation shared by the package command and the paper benchmark script. |
| `models/azure_completion/` | Azure OpenAI adapters shared by teacher compression and downstream scoring. |
| `tasks/distillation/`, `tasks/classifier_training/`, `tasks/benchmark_evaluation/` | Paper teacher compression, classifier training, benchmark generation and scoring. These tasks run through the reproduction launchers. |
| `tasks/precheck/` | Checks the first indexed compression result, a labeled training sample and the first downstream benchmark input row. The batch reuses its first compression result. |
| `conf/config.yaml` | Batch default checkpoint, dataset aliases and canonical component identities. The package command reads the checkout file or the copy bundled in the wheel. |
| `base/prompt_compression/runtime/` | Batch arguments, dispatch, result paths, configuration, manifests and continuation of standalone benchmark output. |
| `scripts/benchmark_reproduction/` | Published paper reproduction commands. The collection, training and evaluation launchers call their corresponding installed implementations. See the reproduction guide for the current script paths and required inputs. |
| `scripts/security_training/` | SecurityLingua method usage and its separate label filtering and classifier training workflow. |
| `data/` | Suggested inputs for the benchmark shell scripts. Place prepared benchmark JSON here or set `LLMLINGUA_DATA_ROOT` to an absolute input directory. |
| `experiment/` | Local run output. The batch command creates it on first use and the benchmark shell scripts use it as their default destination. |
| `scripts/examples/` | Notebooks for public API use cases, including retrieval, code, chain-of-thought, meetings and LLMLingua-2. |
| `tests/` | Offline checks and checkpoint-backed exact-output tests. |
| `assets/illustrations/prompt_compression/` | Diagrams and other assets referenced by the README and paper documentation. |
| `.github/` | GitHub issue and pull-request templates, dependency updates, test workflow and package release. |
| `.agents/` and `AGENTS.md` | Optional local EverResearch instructions and shared skill links. |

The root contains entry-point documentation, build and quality configuration, and the license. The API guide lives under `doc/code/`, and repository policies live under `doc/knowledge/community/`. Package components use the `llmlingua` namespace so wheels can install them alongside Hugging Face's separate `datasets` package. Each evaluation script has a distinct benchmark, downstream prompt or metric. Benchmark evaluators share their metric module and the Azure adapter.

## Batch compression

Run from an installed checkout with your chosen Python interpreter. The command consumes a UTF-8 JSON array. Each row carries an integer-compatible `idx` and a text field selected by `--load_key`. The text may be a string, a list of strings or null. Null rows are skipped. Other fields, such as reference summaries or answers, are copied to the compressed result for the next stage.

```bash
python -m llmlingua compress --dataset meetingbank \
  --load_origin_from data/meetingbank_short/meetingbank_test_3qa_pairs_summary_formated.json \
  --compression_rate 0.33 --force_tokens '\n,?,!,.' --show-config
```

Remove `--show-config` to run and use `--limit N` to process the first N non-null rows. Use `--model_revision` to select and record a specific Hugging Face checkpoint. The command prints the run directory. Pass that directory to `python -m llmlingua show PATH` to read its manifest, configuration and compressed rows. Each invocation creates an independent run within its dataset, model, task and purpose. For example, a MeetingBank run uses `experiment/meeting_bank/llmlingua_2_xlm_roberta_large_meetingbank/compression/transcript_compression/executions/<run-id>/`. Pass either the current directory or its previously documented path to `show`. A run with eligible input validates its first sample before continuing. The manifest records failures, and a successful precheck records the first sample ID. Add `--precheck` to run only that sample and inspect its saved output. The result file `artifacts/compressed_prompts.json` uses the same indexed-object format as the original benchmark compression command. Readers can use it as the downstream evaluator's `--load_prompt_from`.

Input paths on the command line are relative to the caller's working directory. The editable package uses its checkout's `experiment/` directory. A wheel uses the LLMLingua checkout containing the working directory. For a wheel run elsewhere, supply `--experiment-root` to choose the destination. The standalone paper command accepts an explicit `--save_path` and skips existing result IDs when resumed.

## Environment and checks

`make install` installs the checkout into the selected Python environment. The baseline package uses PyTorch, Transformers, Accelerate, tiktoken and NLTK. The GPT-3.5 token counter obtains its encoding through tiktoken. Workflows using NLTK sentence splitting need the appropriate Punkt resource. The paper workflows have separate optional data, tokenization, evaluation and training dependencies.

Run `python -m pytest -q tests/test_batch_compression.py` for local batch and tokenizer checks. `python -m pytest --collect-only -q` lists both local and checkpoint-backed cases. `make test` runs the full suite, including model-backed cases that need their checkpoints and tokenizer resources. The checkpoint-backed cases load their models during test class setup.

Parameters and precedence are described in the [configuration reference](conf.md). The [maintenance record](maintenance.md) gives the findings and validation scope for this structure change.
