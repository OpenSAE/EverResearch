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

- **Original project** [LLMLingua](https://github.com/microsoft/LLMLingua)
- **Source revision** [`01b9e9481d73`](https://github.com/microsoft/LLMLingua/tree/01b9e9481d7395e1e83a48df4a062b11f6304325)
- **Paper** [LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models](https://aclanthology.org/2023.emnlp-main.825/) · EMNLP 2023
- **Authors** Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, Lili Qiu
- **Original source archive** [llmlingua.zip](third_party/upstream/llmlingua.zip)
- **Archive SHA-256** `1216ac683e1a0e1061559b649a97146d71dd97a766be729685a6aec0c020a69d`

### Before organization

```text
LLMLingua/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── dependabot.yml
│   └── workflows/
├── .gitignore
├── .pre-commit-config.yaml
├── CODE_OF_CONDUCT.md
├── DOCUMENT.md
├── LICENSE
├── Makefile
├── README.md
├── SECURITY.md
├── SUPPORT.md
├── Transparency_FAQ.md
├── examples/
│   ├── CoT.ipynb
│   ├── Code.ipynb
│   ├── LLMLingua2.ipynb
│   ├── OnlineMeeting.ipynb
│   ├── RAG.ipynb
│   ├── RAGLlamaIndex.ipynb
│   └── Retrieval.ipynb
├── experiments/
│   ├── llmlingua2/
│   └── securitylingua/
├── images/
│   ├── LLMLingua-2.png
│   ├── LLMLingua.png
│   ├── LLMLingua_demo.png
│   ├── LLMLingua_framework.png
│   ├── LLMLingua_logo.png
│   ├── LLMLingua_motivation.png
│   ├── LongLLMLingua.png
│   ├── LongLLMLingua_Motivation.png
│   └── motivation.png
├── llmlingua/
│   ├── __init__.py
│   ├── prompt_compressor.py
│   ├── utils.py
│   └── version.py
├── pyproject.toml
├── setup.cfg
├── setup.py
└── tests/
    ├── test_llmlingua.py
    ├── test_llmlingua2.py
    └── test_longllmlingua.py
```

### After organization

```text
llmlingua/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── dependabot.yml
│   └── workflows/
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── LICENSE
├── Makefile
├── README.md
├── assets/
│   └── illustrations/
├── base/
│   └── prompt_compression/
├── conf/
│   ├── config.yaml
│   └── tasks/
├── datasets/
│   ├── __init__.py
│   ├── classifier_training/
│   ├── indexed_prompts/
│   ├── prompt_annotation/
│   └── token_classification/
├── doc/
│   ├── README.md
│   ├── code/
│   ├── conf.md
│   ├── datasets.md
│   ├── environment/
│   ├── experiment.md
│   ├── knowledge/
│   ├── maintenance.md
│   ├── models.md
│   └── tasks.md
├── models/
│   ├── __init__.py
│   ├── azure_completion/
│   └── transformer_compression/
├── pyproject.toml
├── scripts/
│   ├── benchmark_reproduction/
│   ├── examples/
│   └── security_training/
├── setup.cfg
├── setup.py
├── tasks/
│   ├── __init__.py
│   ├── benchmark_evaluation/
│   ├── classifier_training/
│   ├── compression/
│   ├── distillation/
│   └── precheck/
├── tests/
│   ├── test_batch_compression.py
│   ├── test_classifier_compression.py
│   ├── test_long_context_compression.py
│   └── test_prompt_compression.py
└── third_party/
    └── upstream/
        └── llmlingua.zip
```
