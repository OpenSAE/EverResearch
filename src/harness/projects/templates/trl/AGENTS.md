# AGENTS.md

## Repository-specific guidance

### Main code vs experimental code

The repository is separated into **main code** and **experimental code**.

* **Main code** should remain stable, consistent, and well-tested.
* **Experimental code** may be less stable and may contain inconsistent patterns or limited testing.

Small non-invasive improvements that make experimental code more consistent with the main codebase are encouraged, but avoid large refactors.

### Paper implementations

If a PR implements a method, algorithm, or training approach from a research paper, it must also add a corresponding subsection to [the paper index](doc/code/reference/source/paper_index.md).

When reviewing such PRs, ensure that [the paper index](doc/code/reference/source/paper_index.md) was updated.

### Code duplication and consistency

Trainers in this repository are **self-contained by design**. Shared logic (generation, reward computation, metric logging, weight syncing, etc.) is deliberately duplicated across trainers rather than abstracted into a shared base class.

This is intentional: each trainer must be readable, modifiable, and evolvable in isolation. The base class (`_BaseTrainer`) provides only minimal utilities (model card generation). Everything else — vLLM generation paths, `_get_per_token_logps_and_entropies`, `_calculate_rewards`, `_prepare_inputs`, metric logging — is copied in full.

**The tradeoff**: duplication is accepted, but **consistency is mandatory**. When the same logic appears in multiple trainers, the duplicated blocks must stay aligned:

- Same variable names (`self._last_loaded_step`, `self._metrics[mode]`, …)
- Same control flow structure (if/elif/else branches in the same order)
- Same comments (word-for-word when the logic is identical)
- Divergences only where the trainer's semantics require it (e.g., GRPO extracts logprobs from vLLM, RLOO discards them)

**Consistency over correctness**: this is a strong requirement. When duplicating code, reproduce it exactly — even if you believe the original has a bug. Do not silently fix the issue in your copy. Instead, keep your copy consistent with the source and report the problem so it can be fixed across all trainers in a dedicated PR. A correct-but-inconsistent codebase is harder to maintain than a consistently-wrong one that can be fixed in a single sweep.

**When modifying duplicated code**: if you change a pattern that exists in multiple trainers (e.g., the vLLM generation path in `_generate_single_turn`), apply the same change to all other trainers. A fix in GRPO often implies the same fix in RLOO, and vice versa. Not propagating a change is a bug.

Find every copy by grepping a distinctive line of the block:

```sh
grep -rn "self._last_loaded_step" tasks/training/ tasks/experimental/
```

After propagating, diff the corresponding regions to confirm they stayed aligned:

```sh
diff <(sed -n '/def _generate_single_turn/,/def /p' tasks/training/grpo_trainer.py) \
     <(sed -n '/def _generate_single_turn/,/def /p' tasks/training/rloo_trainer.py)
```

Remaining diffs must all be semantic divergences, not drift.

**When reviewing**: if a PR touches duplicated logic, verify that all copies are updated consistently. A common mistake is fixing one trainer and forgetting the others.

### Simplicity

This codebase values **leanness and simplicity above all**. Prefer straightforward, inline code over abstractions, helpers, or utilities — even at the cost of some robustness or generality.

Concretely:

- Do not add layers of indirection (registries, factory patterns, plugin systems). A contributor should be able to read a trainer top to bottom and understand the full flow.
- Prefer a simple implementation that covers 90% of cases over a complex one that covers 100%. A function that handles the common path in 20 lines is better than a catch-all that handles every edge case in 80.
- Do not add defensive code, fallback paths, or configuration options "just in case". Only handle cases that actually exist today.
- Avoid `hasattr` and `getattr`. Their use is almost always a symptom of overly defensive programming or a disguised version check (e.g., "this attribute was added in version X"). Instead, either drop the conditional entirely or express the version check explicitly with a version comparison. There is nearly always a cleaner alternative.
- When in doubt, prefer less code. Every new function, parameter, or branch is maintenance burden. The best abstraction is often no abstraction.

### Tests

Tests exercise real objects: a tiny model from `trl-internal-testing`, a real tokenizer, config, and dataset. Do not use `SimpleNamespace`, `MagicMock`, `object.__new__` (building an instance without its `__init__`), or monkeypatched internals as stand-ins: they only have what the test author thought of, so the test keeps passing when the real code changes. Mock only what cannot run in the test environment, like a remote server.

Test behavior through the public API (the trainer, its config, public functions) rather than private methods: a test that calls a private method usually has to build the object around it by hand, and it breaks on any refactor of the internals. Call a private function directly only when its behavior cannot be reached deterministically otherwise, such as a pure helper.

Tests default to what most users run. They train on a conversational dataset rather than a standard one, unless the test is about dataset formats, and tests of online trainers (GRPO, RLOO, …) pass a reward function such as `str_length_reward`, not a reward model, unless the test is about reward models.

There are no `slow` tests: use tiny models, and put tests that need several GPUs in `tests/integration/distributed/`. Tests that need an optional dependency or specific hardware are gated by the `require_*` decorators in `tests/fixtures/environment.py`, so they skip where they cannot run.

A test parametrized over models or chat templates gives each case an id, and a model keeps the same id in every test: `pytest.param("trl-internal-testing/tiny-Qwen2ForCausalLM-2.5", id="qwen2.5")`. The id is the model's name in lowercase, hyphen-separated, with the version attached (`qwen2.5-vl`, `llama3.2`, `deepseek-v3-0528`); reuse the one other tests already give that model. A case that sets a chat template on a model is named after the template (`qwen3.8-v2`), since one model can carry several.

### Issues and assignment

Before working on an issue, check its assignees. If it is assigned to someone other than the user you are working for, do not open a PR that fixes it: tell the user, and suggest asking the assignee in the issue first.

## Documentation

Follow the [contribution guide’s documentation conventions](CONTRIBUTING.md#documentation-conventions) for docstrings and paper links.

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

- **Original project** [TRL](https://github.com/huggingface/trl)
- **Source revision** [`23721a1a706f`](https://github.com/huggingface/trl/tree/23721a1a706fa04254f1bf6a68ee2482599a0b97)
- **Paper** No dedicated paper
- **Authors** Leandro von Werra, Younes Belkada, Lewis Tunstall, Edward Beeching, Tristan Thrush, Nathan Lambert, Shengyi Huang, Kashif Rasul, Quentin Gallouédec, Amine Dirhoussi, Albert Villanova del Moral, Sergio Paniego Blanco
- **Original source archive** [trl.zip](third_party/upstream/trl.zip)
- **Archive SHA-256** `4e0a0d891d9eb1699ad579e773be66dd6bf1a228b1f0338f84207a56e647de82`

### Before organization

```text
trl/
├── .agents/
│   └── skills/
├── .ai/
│   └── AGENTS.md
├── .cursor/
│   └── BUGBOT.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── actions/
│   ├── codeql/
│   ├── dependabot.yml
│   ├── labeler.yml
│   ├── release.yml
│   └── workflows/
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CITATION.cff
├── CLAUDE.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.in
├── MIGRATION.md
├── Makefile
├── README.md
├── RELEASE.md
├── SECURITY.md
├── VERSION
├── assets/
│   ├── logo-dark.png
│   └── logo-light.png
├── docker/
│   ├── trl/
│   └── trl-dev/
├── docs/
│   └── source/
├── examples/
│   ├── README.md
│   ├── async_distillation_math/
│   ├── async_distillation_mopd/
│   ├── async_grpo_harbor/
│   ├── async_grpo_math/
│   ├── async_grpo_s3_aggregation/
│   ├── datasets/
│   ├── deepspeed_configs/
│   ├── distillation_data_analysis_env/
│   ├── dpo_reduce_hallucinations/
│   ├── fsdp_configs/
│   ├── gold_chatbot_arena/
│   ├── gold_qwen3_vl/
│   ├── grpo_2048/
│   ├── grpo_browsergym/
│   ├── grpo_carla/
│   ├── grpo_catch/
│   ├── grpo_continuous_batching/
│   ├── grpo_echo/
│   ├── grpo_harbor/
│   ├── grpo_ministral3_vl/
│   ├── grpo_multi_env/
│   ├── grpo_qlora/
│   ├── grpo_qwen3_vl/
│   ├── grpo_rnj_1_instruct/
│   ├── grpo_seta/
│   ├── grpo_sql_agent/
│   ├── grpo_sudoku/
│   ├── grpo_visual_math/
│   ├── grpo_wordle/
│   ├── gspo_math/
│   ├── gspo_visual_math/
│   ├── lfm2_5_moe_research_agent/
│   ├── mpo_visual_preferences/
│   ├── online_dpo_visual_math/
│   ├── rloo_math/
│   ├── rloo_visual_math/
│   ├── sdft_privileged_context/
│   ├── sdpo_math/
│   ├── sft_agent_traces/
│   ├── sft_beam/
│   ├── sft_diffusion_gemma/
│   ├── sft_gemma3/
│   ├── sft_gemma3_vision/
│   ├── sft_gpt_oss_chess/
│   ├── sft_inkling_2_mini_clocks/
│   ├── sft_ministral3_vl/
│   ├── sft_mistral_large_4/
│   ├── sft_muse_spark_open/
│   ├── sft_nemotron_3/
│   ├── sft_qlora/
│   ├── sft_qwen3_8b_1m_context/
│   ├── sft_qwen3_vl/
│   ├── sft_tool_calling/
│   ├── sft_visual_chat/
│   ├── tail_sft_gsm8k/
│   └── xtoken/
├── pyproject.toml
├── scripts/
│   ├── add_copyrights.py
│   ├── check_chat_templates.py
│   ├── generate_harmony_dataset.py
│   ├── generate_tiny_models/
│   ├── generate_toolcall_dataset.py
│   ├── generate_zen_dataset.py
│   ├── generate_zen_image_dataset.py
│   └── generate_zen_multi_image_dataset.py
├── skills/
│   └── trl-training/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── data/
│   ├── distributed/
│   ├── experimental/
│   ├── invariant/
│   ├── test_activation_offloading.py
│   ├── test_async_grpo_trainer.py
│   ├── test_base_config.py
│   ├── test_callbacks.py
│   ├── test_chat_template_utils.py
│   ├── test_cli.py
│   ├── test_cli_utils.py
│   ├── test_data_utils.py
│   ├── test_distillation_trainer.py
│   ├── test_dpo_trainer.py
│   ├── test_examples_index.py
│   ├── test_grpo_trainer.py
│   ├── test_kernels.py
│   ├── test_kto_trainer.py
│   ├── test_model_utils.py
│   ├── test_reward_trainer.py
│   ├── test_rewards.py
│   ├── test_rich_progress_callback.py
│   ├── test_rloo_trainer.py
│   ├── test_selective_activation_checkpointing.py
│   ├── test_sft_trainer.py
│   ├── test_utils.py
│   ├── test_vllm_client_server.py
│   ├── testing_constants.py
│   └── testing_utils.py
└── trl/
    ├── __init__.py
    ├── _compat.py
    ├── _lazy_module.py
    ├── accelerate_configs/
    ├── chat_template_utils.py
    ├── chat_templates/
    ├── cli/
    ├── data_utils.py
    ├── distributed.py
    ├── experimental/
    ├── extras/
    ├── generation/
    ├── import_utils.py
    ├── kernels/
    ├── models/
    ├── py.typed
    ├── rewards/
    ├── scripts/
    ├── templates/
    └── trainer/
```

### After organization

```text
trl/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── assets/
│   ├── configuration/
│   ├── container/
│   ├── identity/
│   ├── package/
│   └── templates/
├── base/
│   ├── experiment_runner.py
│   ├── training_runs.py
│   └── transformers_reinforcement_learning/
├── conf/
│   └── config.toml
├── datasets/
│   └── preparation/
├── doc/
│   ├── README.md
│   ├── code/
│   ├── conf.md
│   ├── environment/
│   ├── experiment.md
│   ├── knowledge/
│   ├── maintenance.md
│   └── tasks.md
├── main.py
├── models/
│   ├── adapters/
│   ├── block_diffusion/
│   ├── causal_language_model/
│   ├── conditional_generation/
│   ├── fixture_support/
│   └── sequence_classification/
├── pyproject.toml
├── scripts/
│   ├── add_copyrights.py
│   ├── check_chat_templates.py
│   ├── examples/
│   ├── experimental_training.py
│   ├── generate_harmony_dataset.py
│   ├── generate_toolcall_dataset.py
│   ├── generate_zen_dataset.py
│   ├── generate_zen_image_dataset.py
│   └── generate_zen_multi_image_dataset.py
├── setup.py
├── tasks/
│   ├── advantage_alignment/
│   ├── configuration/
│   ├── experimental/
│   ├── experimental_parameters/
│   ├── kernels/
│   ├── precheck/
│   ├── rewards/
│   └── training/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   ├── integration/
│   ├── product/
│   ├── test_chat_template_utils.py
│   ├── test_examples_index.py
│   ├── test_reward_trainer.py
│   └── test_sft_trainer.py
└── third_party/
    └── upstream/
        └── trl.zip
```
