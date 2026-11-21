# Project maintenance record

## Component layout

The central project check first reported seven violations. The checkout now has separate directories for datasets, models, tasks, and defaults. Setuptools publishes these physical source directories at the existing `FlagEmbedding` imports and Python module commands.

| Responsibility | Change and evidence |
| --- | --- |
| Runtime | `base/flag_embedding/` provides the public API, dispatch and shared interfaces. Imports outside the checkout passed in the refreshed editable installation and with the installed wheel files. |
| Datasets | `datasets/evaluation/` holds the common and benchmark-specific loaders. `datasets/fine_tuning/` holds the training datasets and collators. The offline retrieval tests read generated corpora, queries and judgments through the Custom, BEIR and BRIGHT commands. |
| Models | `models/embedding/` and `models/ranking/` hold inference implementations. The training model families are in `models/embedding_training/` and `models/ranking_training/`. The package preserves legacy names, including the decoder-only ranking backbone imports. The retrieval suite uses tiny local BERT checkpoints. |
| Tasks | `tasks/evaluation/` contains the benchmark commands, `tasks/retrieval/` contains shared search and scoring, and `tasks/embedding_tuning/` and `tasks/ranking_tuning/` contain the training commands. The existing automatic retrieval precheck and ranking readback passed for the three offline retrieval workflows. Help ran for seven evaluation and seven training commands. MTEB and AIR-Bench require their optional backend packages. |
| Parameters | `conf/config.json` supplies the shared retrieval and reporting defaults through the ordinary evaluation argument classes. Model and dataset selection and explicit command-line overrides continue to use the existing argument interface. Defaults were loaded by the editable installation and wheel. |
| Experiments | The experiment checker returned zero violations and found zero active runs. Three existing result archives retain the FiQA similarity, FiQA retrieval, and synthetic retrieval runs. The normal evaluation commands still read their existing rankings and reports. |
| Scripts, tests and documentation | The 24 decoder-only presets now live in `automatic/` and `direct/` under their original workflow directories. The ranking presets now import the actual shared ranking example. All 24 dispatched to their model-call doubles as both scripts and modules. The offline suite passed 17 tests with two skips for optional MTEB support and Transformers 5. |

The central project check inspected 1,680 paths and returned zero violations. The remaining execution coverage includes automatic prechecks for training and the two external benchmarks, canonical manifests for new experiments, and fresh runs with published weights.

## Retrieval prechecks

The shared retrieval evaluator now scores one query and document per selected split before full retrieval, and checks the ranking through the ordinary writer and reader. A requested reranker checks one candidate before a new reranking workload. BEIR preserves sub-dataset metadata in this check. BRIGHT uses the active split's document exclusions. Custom evaluation also checks its local file headers and retains its independent `--precheck_only` command. The result reader still serves metric requests from existing complete rankings.

| Responsibility | Current evidence and remaining coverage |
| --- | --- |
| Runtime | The installed package and its precheck import resolved to the current checkout from a separate working directory. The shared evaluator runs through the public Custom, BEIR and BRIGHT module commands in the offline suite. |
| Datasets | Custom validates the first nonempty corpus, query and judgment records. BRIGHT checks the active split's exclusions when selecting the sample. BEIR's generated CQA sub-datasets exercise separate corpus caches. Published dataset coverage in this pass is limited to the archived FiQA readback. |
| Models | Generated BERT weights exercise local CPU embedding and reranking through the existing factories. The bound published BGE directories contain tokenizer and configuration files. Published-weight comparison remains available in the archived FiQA evidence. |
| Tasks | The automatic check is exercised through Custom, BEIR and BRIGHT. MIRACL, MLDR, MS MARCO and MKQA reach the same evaluator through the base runner. MTEB and AIR-Bench use external benchmark runners. Their prechecks, fine-tuning prechecks and independent research reproduction prechecks are still open. |
| Parameters | BRIGHT rejects a zero retrieval candidate count before creating a rankings directory. Custom verifies its standalone precheck and reuses saved rankings after reporting cutoffs change. BEIR rebuilds a missing reranking file from saved retrieval results. The parameter and evaluation pages describe the effect. |
| Experiments | The archive commands opened both FiQA reports and the synthetic retrieval metrics. The central experiment scan passed with zero active runs. New project launchers still need a writer for effective configuration, manifests and declared outputs. |
| Scripts, tests and documentation | The offline suite passed 17 tests with two skips for MTEB and Transformers 5 coverage. Each decoder-only example directory has twelve launchers that select device, loading mode and model type through a shared implementation. The benchmark guide describes the shared precheck and cache behavior. |

The central layout scan passed with 1,637 paths and no violations.

## Earlier layout migration

This pass inspected the editable checkout at upstream revision `897baa6`, including its existing changes and local results. The installed `FlagEmbedding` namespace and `python -m FlagEmbedding.evaluation.*` commands retain their existing names. The existing local Python binding now points to the new package source through the refreshed editable install.

### Layout follow-up

The full-tree checker reported no violations after the remaining source, documentation, example, and research paths were migrated. The independent experiment checker also passed and found zero active runs.

| Previous location | Current location and reader | Check |
| --- | --- | --- |
| `base/flag_embedding/abc/`, fine-tuning and inference families, evaluation adapters, and compatibility modules | [The installable source tree](../base/flag_embedding/) uses names that describe each responsibility. [Setuptools](../setup.py) maps them to the established `FlagEmbedding` imports and module commands. | Built a wheel and source archive. The editable installation and a separate wheel installation imported the legacy abstract API, benchmark helpers, embedding and ranking modules, and opened command help for custom evaluation and multifunctional BGE fine-tuning. |
| `docs/` | [BGE Sphinx site](code/model_documentation/README.md). The [documentation workflow](../.github/workflows/documentation.yml) uses the new source and build paths. | Built HTML from the new source location and verified all three downloaded benchmark launchers. The build reported eight warnings covering six optional benchmark API imports and two existing documentation notices. The local Makefile and CI target agree on `tmp/documentation_build/.build/html`. |
| `examples/evaluation/`, `examples/inference/`, and `examples/finetune/` | [Shell and Python examples](../scripts/examples/README.md) use the same package APIs and named benchmark commands. The 24 decoder-only device and loading presets share two implementations. | Parsed all shell launchers. Custom and BEIR launchers reported their usage from the relocated paths. |
| `examples/finetune/*/example_data/` | [Training examples](../assets/training_examples/) hold the original JSON Lines inputs. Fine-tuning recipes point to the new locations and retain the two DeepSpeed configurations. | Checked the local path references from the recipe directories. |
| `research/` | [Upstream research releases](../third_party/README.md) keep self-contained upstream reproduction packages and their internal paths. The navigation maps previous checkout commands to the moved worktrees, and the MTEB recipe points to the moved in-context examples. | Compared all 598 files with the upstream commit byte-for-byte. |

The full test suite collected 27 tests. The offline suite passed 17 and skipped two. The skipped tests require optional MTEB support and Transformers 5 respectively. Editable imports were checked from a working directory outside the project. In the project's parent directory, the checkout name can shadow the editable package. The wheel installation passed the same smoke checks from that parent directory.

The current task evidence covers the custom retrieval precheck and its rejection of invalid local inputs, ranking and metrics readback, and the existing BEIR and BRIGHT regression cases. Automatic prechecks outside custom retrieval and manifest creation by the evaluation launchers remain open. The releases under `third_party/` were checked for source preservation.

### Source, documents, and archived inputs

| Original location | Current location and reason | Evidence |
| --- | --- | --- |
| `FlagEmbedding/` | `base/flag_embedding/` owns the installable API, inference implementations, fine-tuning, and evaluation. `setup.py` maps the public import name to this source. | Built a source archive and wheel. A wheel install outside the checkout imported the API and opened the custom evaluation and encoder fine-tuning command help. |
| `FlagEmbedding/evaluation/mkqa/utils/` | The package declaration now includes its two evaluation helpers. | The wheel install imported the text normalization helper. |
| `dataset/README.md`, `README_zh.md`, `docs/PROJECT_STRUCTURE.md` | `doc/datasets.md`, `doc/knowledge/readme_chinese.md`, and `doc/code/repository_structure.md` provide local navigation through `doc/README.md`. | Updated reader entry points and source path references. |
| `Tutorials/` | `scripts/tutorials/` contains 34 runnable notebooks and their settings. Its index records the topic order. The roadmap is grouped with project illustrations. | Parsed the relocated notebooks and updated references to the affected examples, images, and DeepSpeed settings. |
| `imgs/` and the reference examples under the MTEB and AIR-Bench evaluation packages | `assets/illustrations/project/` and `assets/benchmark_examples/` contain the original images, CSVs, and JSONL files and their documentation. | Python imports stayed under the package source. The reader gets the example format and paths from each asset's README. |
| `tests/test_imports_v5.py` | `tests/test_transformers_import_compatibility.py` records the behavior tested. | Root test collection includes the same cases and the new local precheck regression. |
| `FlagEmbedding.egg-info/` and `Manifest.in` | Packaging metadata was moved to `tmp/packaging/`. The former manual manifest referred to visual model files outside the main package. The visual research package carries its own packaging files. | The setuptools source archive and wheel build from the current package mapping. |
| Previous `experiment/fiqa/` and `experiment/synthetic_text/` results | Three groups in `assets/history_experiment/` keep their original project-relative paths and file contents in local archives. | Verified 64 members byte-for-byte. Reopened both FiQA results with the original readers and recomputed the similarity and retrieval checks. |

### Component checks

| Responsibility | Entry and verified behavior | Remaining work |
| --- | --- | --- |
| Runtime | Editable and wheel installs resolve `FlagEmbedding`, including MKQA utilities and the custom retrieval precheck. The custom evaluation and encoder fine-tuning help work outside the checkout. | The other public training and evaluation entries need equivalent runtime coverage. |
| Datasets | The custom loader selects local `corpus.jsonl`, query, and relevance records. The normal command rejects a missing split before model loading and an invalid sample grade before creating rankings. The FiQA readers checked identities and relevance against the local source. | The checks cover custom data and saved FiQA evidence. Other benchmark adapters need their own input validation evidence. |
| Models | Existing embedding and reranking factories retained their imports. The local tests exercise small BERT checkpoints and verify finite retrieval scores. The archived runs document the actual versions of the published FiQA models. | No full training run or fresh published-checkpoint inference was performed in this pass. |
| Tasks | The public custom command automatically checks one query, one document, one relevance record, and an isolated ranking round trip for each selected split when a dataset needs new rankings. `--precheck_only` runs the same check and exits. Reused rankings still support metric readback. | BEIR, BRIGHT, MTEB, other benchmarks, fine-tuning, and independent research programs need their own automatic task prechecks. |
| Parameters | The custom command accepts `--precheck_only`. Existing model, dataset, and output flags retained their behavior, including saved ranking reuse when metric cutoffs change. The evaluation recipe explains the new flag. | Example launchers still use their existing output conventions and the CLI dataclasses provide their defaults. |
| Experiments | The historical FiQA similarity reader confirmed a 12-by-46 score matrix, 768-dimensional embeddings, and a maximum recomputed score deviation of 0.000244. The FiQA retrieval reader verified both ranking depths, recomputed nDCG@10 of 0.75304 and 0.69571, and obtained Recall@100 of 1.0 for both stages. | No active execution records were created. The existing shell launchers lack canonical run manifests. |
| Scripts, tests, and documentation | Project navigation points to the moved assets and tutorial notebooks. The offline suite exercised local retrieval, saved results, and precheck success and failure. | The Sphinx tree, project evaluation/inference examples, and independent research recipes retain their existing source directories and need complete migration and related compatibility checks. |

### Central checks

The independent experiment checker exited successfully with zero active runs. Historical archive validation covers the 64 archived files separately. The layout checker exited with status 1 after inspecting 529 paths. It reported 41 violations across public package spellings, including benchmark names and CamelCase modules, and the `docs/`, `examples/`, and `research/` roots. Those paths serve package imports, the configured Sphinx build, user-facing launch recipes, and published paper reproductions.

In the bound Transformers 4.57.6 environment the offline suite passed 17 tests. It skipped the MTEB test because the optional `mteb` package was absent and the Transformers 5-only check because of the installed version.
