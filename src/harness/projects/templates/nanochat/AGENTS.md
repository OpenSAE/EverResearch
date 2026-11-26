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

- **Original project** [nanochat](https://github.com/karpathy/nanochat)
- **Source revision** [`92d63d4e8bb4`](https://github.com/karpathy/nanochat/tree/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd)
- **Paper** No dedicated paper
- **Authors** Andrej Karpathy
- **Original source archive** [nanochat.zip](third_party/upstream/nanochat.zip)
- **Archive SHA-256** `c8f1051ebf2ca5eff005106bcab008fc74e1a3bd61893a305da0f2a4f6932991`

### Before organization

```text
nanochat/
├── .claude/
│   └── skills/
├── .gitignore
├── .python-version
├── LICENSE
├── README.md
├── dev/
│   ├── LEADERBOARD.md
│   ├── LOG.md
│   ├── estimate_gpt3_core.ipynb
│   ├── nanochat.png
│   ├── repackage_data_reference.py
│   ├── scaling_analysis.ipynb
│   └── scaling_laws_jan26.png
├── nanochat/
│   ├── __init__.py
│   ├── checkpoint_manager.py
│   ├── common.py
│   ├── core_eval.py
│   ├── dataloader.py
│   ├── dataset.py
│   ├── engine.py
│   ├── execution.py
│   ├── flash_attention.py
│   ├── fp8.py
│   ├── gpt.py
│   ├── loss_eval.py
│   ├── optim.py
│   └── tokenizer.py
├── pyproject.toml
├── runs/
│   ├── miniseries.sh
│   ├── runcpu.sh
│   ├── scaling_laws.sh
│   └── speedrun.sh
├── scripts/
│   ├── base_eval.py
│   ├── base_train.py
│   ├── chat_cli.py
│   ├── chat_eval.py
│   ├── chat_rl.py
│   ├── chat_sft.py
│   ├── infer_bench.py
│   ├── tok_eval.py
│   └── tok_train.py
├── tasks/
│   ├── arc.py
│   ├── common.py
│   ├── gsm8k.py
│   ├── humaneval.py
│   ├── mmlu.py
│   └── smoltalk.py
├── tests/
│   ├── test_attention_fallback.py
│   ├── test_engine.py
│   ├── test_execution.py
│   ├── test_optim.py
│   ├── test_tasks.py
│   └── test_tokenizer.py
└── uv.lock
```

### After organization

```text
nanochat/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitignore
├── .python-version
├── AGENTS.md
├── LICENSE
├── README.md
├── assets/
│   └── figures/
├── base/
│   ├── chat_runtime/
│   ├── commands/
│   └── compatibility/
├── conf/
│   └── config.json
├── datasets/
│   ├── climbmix_corpus/
│   ├── conversations/
│   └── tokenization/
├── doc/
│   ├── README.md
│   ├── environment/
│   ├── experiment.md
│   ├── knowledge/
│   └── maintenance.md
├── models/
│   └── transformer/
├── pyproject.toml
├── scripts/
│   ├── estimate_core.ipynb
│   ├── miniseries.sh
│   ├── run_cpu.sh
│   ├── scaling_analysis.ipynb
│   ├── scaling_laws.sh
│   └── speed_run.sh
├── setup.cfg
├── tasks/
│   ├── __init__.py
│   ├── arc/
│   ├── base_training/
│   ├── common/
│   ├── conversation/
│   ├── evaluation/
│   ├── fine_tuning/
│   ├── inference/
│   ├── precheck/
│   └── tokenization/
├── tests/
│   ├── test_attention_fallback.py
│   ├── test_engine.py
│   ├── test_execution.py
│   ├── test_optimizer.py
│   ├── test_tasks.py
│   └── test_tokenizer.py
├── third_party/
│   └── upstream/
│       └── nanochat.zip
└── uv.lock
```
