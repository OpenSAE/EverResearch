# Project maintenance

## Purpose and main functions

Use this reference to find the project entry points and maintain their dependencies.

## Scope

Applies to work on this template. Start with README.md and doc/README.md for normal commands and setup.

<!-- everresearch:search -->
## Locate projects and files

Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.
<!-- /everresearch:search -->

<!-- everresearch:mode -->
## Choose the maintenance mode

### Purpose and main functions

Use the project setting to select its maintenance guide and structure checker.

### Scope

Use this section for project maintenance, checking the online connection, or running an offline structure check.

Start by reading `.everresearch/mode.toml`. Its `enabled` setting selects this project's maintenance mode. Follow the user's choice and obtain authorization before changing it.

- **`enabled = false` selects offline maintenance.** Use the project's [offline operations guide](.everresearch/offline/operations.md). It explains how to plan, carry out, and finish maintenance using the project's files, commands, tests, and data.
- **`enabled = true` selects online maintenance.** Run `python -IS .everresearch/maintain.py status` first. When it prints `online`, read the central guide at the reported path. Follow that guide to the operations manual, shared skills, and central checks in the EverResearch repository. If the status command fails, report the cause and pause work that requires central maintenance until the user restores the connection or selects offline mode.
- **A missing or invalid setting blocks maintenance.** Report the problem and continue once the setting has been corrected or the user has chosen a mode.

When a structure check is authorized, run `python -IS .everresearch/maintain.py check` from the project root. The command runs the checker for the selected mode. Follow the project README for installation, training, prechecks, and reading results.
<!-- /everresearch:mode -->

## Original project and template layout

- **Original project** [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding)
- **Source revision** [`897baa67c0ff`](https://github.com/FlagOpen/FlagEmbedding/tree/897baa67c0ffddbfccf4e6776ff55310d67809d4)
- **Paper** [BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation](https://arxiv.org/abs/2402.03216) · arXiv preprint (2024) · associated study
- **Authors** Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, Zheng Liu
- **Original source archive** [flag_embedding.zip](third_party/upstream/flag_embedding.zip)
- **Archive SHA-256** `1e171854dcfc97f17672949b8d9949715f9f91eff1376693e6026cca55cd43d3`

### Before organization

```text
FlagEmbedding/
├── .github/
│   └── workflows/
├── .gitignore
├── FlagEmbedding/
│   ├── __init__.py
│   ├── abc/
│   ├── evaluation/
│   ├── finetune/
│   ├── inference/
│   └── utils/
├── LICENSE
├── Manifest.in
├── README.md
├── README_zh.md
├── Tutorials/
│   ├── 1_Embedding/
│   ├── 2_Metrics/
│   ├── 3_Indexing/
│   ├── 4_Evaluation/
│   ├── 5_Reranking/
│   ├── 6_RAG/
│   ├── 7_Fine-tuning/
│   ├── README.md
│   ├── quick_start.ipynb
│   └── tutorial_map.png
├── dataset/
│   └── README.md
├── docs/
│   ├── Makefile
│   ├── README.md
│   ├── make.bat
│   ├── requirements.txt
│   └── source/
├── examples/
│   ├── README.md
│   ├── evaluation/
│   ├── finetune/
│   └── inference/
├── imgs/
│   ├── BGE_WeChat_Group.png
│   ├── FlagOpen.png
│   ├── bge_logo.jpg
│   ├── cir_candi_1.png
│   ├── cir_candi_2.png
│   ├── cir_query.png
│   └── projects.png
├── research/
│   ├── BGE_Coder/
│   ├── BGE_M3/
│   ├── BGE_Reasoner/
│   ├── BGE_VL/
│   ├── BGE_VL_Screenshot/
│   ├── C_MTEB/
│   ├── LLARA/
│   ├── LM_Cocktail/
│   ├── Long_LLM/
│   ├── MLVU/
│   ├── Matroyshka_reranker/
│   ├── README.md
│   ├── Reinforced_IR/
│   ├── baai_general_embedding/
│   ├── llm_dense_retriever/
│   ├── llm_embedder/
│   ├── llm_reranker/
│   ├── old-examples/
│   ├── reranker/
│   └── visual_bge/
├── scripts/
│   ├── README.md
│   ├── add_reranker_score.py
│   ├── hn_mine.py
│   ├── hn_mine_nv.py
│   └── split_data_by_length.py
├── setup.py
└── tests/
    ├── README.md
    ├── conftest.py
    ├── test_finetune_trainer_compat.py
    ├── test_imports_v5.py
    ├── test_infer_embedder_basic.py
    ├── test_infer_reranker_basic.py
    ├── test_reranker_tokenizer_compat.py
    └── test_tokenizer_pad_compat.py
```

### After organization

```text
flag_embedding/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .github/
│   └── workflows/
├── .gitignore
├── AGENTS.md
├── LICENSE
├── README.md
├── assets/
│   ├── benchmark_examples/
│   ├── illustrations/
│   └── training_examples/
├── base/
│   └── flag_embedding/
├── conf/
│   └── config.json
├── datasets/
│   ├── evaluation/
│   └── fine_tuning/
├── doc/
│   ├── README.md
│   ├── code/
│   ├── conf.md
│   ├── datasets.md
│   ├── environment/
│   ├── experiment.md
│   ├── knowledge/
│   └── maintenance.md
├── models/
│   ├── embedding/
│   ├── embedding_training/
│   ├── ranking/
│   └── ranking_training/
├── scripts/
│   ├── README.md
│   ├── add_reranker_score.py
│   ├── examples/
│   ├── hn_mine.py
│   ├── hn_mine_nv.py
│   ├── split_data_by_length.py
│   └── tutorials/
├── setup.py
├── tasks/
│   ├── embedding_tuning/
│   ├── evaluation/
│   ├── fine_tuning_support/
│   ├── precheck/
│   ├── ranking_tuning/
│   └── retrieval/
├── tests/
│   ├── README.md
│   ├── conftest.py
│   ├── integration/
│   ├── test_finetune_trainer_compat.py
│   ├── test_mteb_evaluation.py
│   ├── test_reranker_tokenizer_compat.py
│   ├── test_retrieval_evaluation.py
│   ├── test_tokenizer_pad_compat.py
│   └── test_transformers_import_compatibility.py
└── third_party/
    ├── README.md
    ├── flag_embedding_research/
    └── upstream/
        └── flag_embedding.zip
```
