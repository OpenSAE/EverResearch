This file provides guidance to AI agents when working with code in this repository.

> **User-facing help → [`doc/code/agent_guide.md`](doc/code/agent_guide.md)** (SO-101 setup, recording, picking a policy, training duration, eval — with copy-pasteable commands).

## Project Overview

LeRobot is a PyTorch-based library for real-world robotics, providing datasets, pretrained policies, and tools for training, evaluation, data collection, and robot control. It integrates with Hugging Face Hub for model/dataset sharing.

## Tech Stack

Python 3.12+ · PyTorch · Hugging Face (datasets, Hub, accelerate) · draccus (config/CLI) · Gymnasium (envs) · uv (package management)

## Development Setup

```bash
uv sync --locked                            # Base dependencies
uv sync --locked --extra test --extra dev   # Test + dev tools
uv sync --locked --extra all                # Everything
git lfs install && git lfs pull             # Test artifacts
```

## Key Commands

```bash
uv run pytest tests -svv --maxfail=10                 # All tests
DEVICE=cuda make test-end-to-end                      # All E2E tests
pre-commit run --all-files                           # Lint + format (ruff, typos, bandit, etc.)
```

## Architecture and public Python packages

- **`scripts/`** — CLI entry points (`lerobot-train`, `lerobot-eval`, `lerobot-record`, etc.), mapped in `pyproject.toml [project.scripts]`.
- **`configs/`** — Dataclass configs parsed by draccus. `train.py` has `TrainPipelineConfig` (top-level). `policies.py` has `PreTrainedConfig` base. Polymorphism via `draccus.ChoiceRegistry` with `@register_subclass("name")` decorators.
- **`policies/`** — Each policy in its own subdir. All inherit `PreTrainedPolicy` (`nn.Module` + `HubMixin`) from `pretrained.py`. Factory with lazy imports in `factory.py`.
- **`processor/`** — Data transformation pipeline. `ProcessorStep` base with registry. `DataProcessorPipeline` / `PolicyProcessorPipeline` chain steps.
- **`datasets/`** — `LeRobotDataset` (episode-aware sampling + video decoding) and `LeRobotDatasetMetadata`.
- **`envs/`** — `EnvConfig` options in `configs.py`; `make_env()` / `make_task_env()` in `factory.py` build the envs. A config's `sim_settings()` maps its options to its `lerobot.sim.integrations.<type>` module's `env_fns()` kwargs.
- **`robots/`, `motors/`, `cameras/`, `teleoperators/`** — Hardware abstraction layers.
- **`types.py`** and **`configs/types.py`** — Core type aliases and feature type definitions.

## Repository Structure (outside `src/`)

- **`tests/`** — Pytest suite organized by module. Fixtures in `tests/fixtures/`, mocks in `tests/fixtures/mocks/`. Hardware tests use skip decorators from `tests/fixtures/utils.py`. E2E tests via `Makefile` write to `tmp/end_to_end/`.
- **`.github/workflows/`** — CI: `quality.yml` (pre-commit), `fast_tests.yml` (one tier per extra, selected by pytest mark, every PR), `full_tests.yml` (all extras + E2E, GPU job runs `-m gpu`, post-approval), `latest_deps_tests.yml` (daily lockfile upgrade), `security.yml` (TruffleHog), `release.yml` (PyPI publish on tags).
- **`doc/code/reference/source/`** — HF documentation (`.mdx` files). Per-policy READMEs, hardware guides, tutorials. Built separately via `doc/code/reference/requirements.txt` and CI workflows.
- **`examples/`** — End-user tutorials and scripts organized by use case (dataset creation, training, hardware setup).
- **`docker/`** — Dockerfiles for user (`Dockerfile.user`) and CI (`Dockerfile.internal`).
- **`benchmarks/`** — Performance benchmarking scripts.
- **Root files**: `pyproject.toml` (single source of truth for deps, build, tool config), `Makefile` (E2E test targets), `uv.lock`, `CONTRIBUTING.md` & `README.md` (general information).

## Notes

- **Mypy**: one ruleset (`[tool.mypy]` in `pyproject.toml`) checks the paths in its `files` setting, except `lerobot.rl`, the vendored `molmoact2_hf_model` and the generated `*_pb2` modules. Run it with `pre-commit run mypy --all-files`. Add type annotations when modifying code.
- **Imports**: prefer top-level imports; relative (`from .sibling import X`) across sibling files within a module, absolute (`from lerobot.module import X`) across modules.
- **Optional dependencies**: many policies, envs, and robots are behind extras (e.g., `lerobot[aloha]`, see `pyproject.toml`). Guard optional imports with `TYPE_CHECKING or _foo_available` at module top + a `require_package(...)` check at use time. Reuse the `_foo_available` flags in `utils/import_utils.py`; don't call `is_package_available`.
- **Video decoding**: datasets can store observations as video files. `LeRobotDataset` handles frame extraction, but tests need ffmpeg installed.
- **Prioritize use of `uv run`** to execute Python commands (not raw `python` or `pip`).
- **Test marks**: Fast Tests runs one tier per extra (`-m base|dataset|hardware|viz`) and the GPU job runs `-m gpu`. A test that needs the `dataset`, `hardware` or `viz` extra must be marked (`pytestmark = pytest.mark.dataset`), otherwise it only runs in `base` and skips there. A test that uses CUDA outside `tests/product/policies` and without `@require_cuda` needs `@pytest.mark.gpu`. Details in CONTRIBUTING.md, "Running Tests".

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

- **Original project** [LeRobot](https://github.com/huggingface/lerobot)
- **Source revision** [`b07adcc5e3ce`](https://github.com/huggingface/lerobot/tree/b07adcc5e3ce42c26a248236dbb3571f84c28c43)
- **Paper** [LeRobot: An Open-Source Library for End-to-End Robot Learning](https://proceedings.iclr.cc/paper_files/paper/2026/hash/c702175bc31584c52c28cc20731db371-Abstract-Conference.html) · ICLR 2026 Poster
- **Authors** Remi Cadene, Simon Alibert, Francesco Capuano, Michel Aractingi, Adil Zouitine, Pepijn Kooijmans, Jade Choghari, Martino Russi, Caroline Pascal, Steven Palma, Dana Aubakirova, Mustafa Shukor, Jess Moss, Alexander Soare, Quentin Lhoest, Quentin Gallouédec, Thomas Wolf
- **Original source archive** [`lerobot.zip`](third_party/upstream/lerobot.zip)
- **Archive SHA-256** `410d022c5df259578ffbee2433411d17723182f61f73b6dc6dc1ebf6465d6091`

### Before organization

```text
lerobot/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   ├── dependabot.yml
│   ├── labeler.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── benchmarks/
│   └── benchmarks.yaml
├── docker/
│   ├── sim/
│   ├── Dockerfile.internal
│   ├── Dockerfile.jetson
│   ├── Dockerfile.policy
│   ├── Dockerfile.rocm
│   ├── Dockerfile.sim
│   ├── Dockerfile.user
│   └── README.md
├── docs/
│   ├── source/
│   └── README.md
├── examples/
│   ├── backward_compatibility/
│   ├── dataset/
│   ├── flux3/
│   ├── isaac_teleop_to_so101/
│   ├── lekiwi/
│   ├── notebooks/
│   ├── omx/
│   ├── phone_to_so100/
│   ├── port_datasets/
│   ├── praxis/
│   ├── remote_inference/
│   ├── rtc/
│   ├── so100_to_so100_EE/
│   ├── training/
│   └── … (1 more entries)
├── media/
│   └── readme/
├── scripts/
│   └── ci/
├── src/
│   └── lerobot/
├── tests/
│   ├── annotations/
│   ├── artifacts/
│   ├── cameras/
│   ├── ci/
│   ├── common/
│   ├── configs/
│   ├── controllers/
│   ├── datasets/
│   ├── distributed/
│   ├── env_server/
│   ├── envs/
│   ├── fixtures/
│   ├── inference/
│   ├── jobs/
│   └── … (37 more entries)
├── utils/
│   ├── check_config_docstrings.py
│   ├── check_docstrings.py
│   ├── check_doctest_list.py
│   └── documentation_tests.txt
├── .dockerignore
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── AGENT_GUIDE.md
├── AGENTS.md
├── AI_POLICY.md
├── CLAUDE.md
├── CODE_OF_CONDUCT.md
├── conftest.py
├── CONTRIBUTING.md
├── docs-requirements.txt
├── LICENSE
├── Makefile
├── MANIFEST.in
├── pyproject.toml
├── README.md
├── SECURITY.md
├── setup.py
└── uv.lock
```

### After organization

```text
lerobot/
├── .everresearch/
│   ├── offline/
│   ├── maintain.py
│   └── mode.toml
├── assets/
│   ├── configuration/
│   ├── hardware/
│   ├── media/
│   ├── network/
│   ├── protocol/
│   ├── simulation/
│   └── templates/
├── base/
│   ├── lerobot_library/
│   └── package_layout.py
├── conf/
│   ├── base/
│   └── config.yaml
├── datasets/
│   ├── commands/
│   ├── lerobot_dataset/
│   ├── preparation/
│   ├── streaming/
│   └── transforms/
├── doc/
│   ├── code/
│   ├── environment/
│   ├── experiment.md
│   ├── maintenance.md
│   └── README.md
├── models/
│   ├── policies/
│   ├── rewards/
│   └── shared/
├── scripts/
│   ├── benchmarks/
│   ├── ci/
│   ├── development/
│   └── examples/
├── tasks/
│   ├── evaluation/
│   ├── policy_rollout/
│   ├── precheck/
│   ├── recording/
│   ├── reinforcement/
│   └── training/
├── tests/
│   ├── fixtures/
│   ├── product/
│   ├── __init__.py
│   └── conftest.py
├── third_party/
│   └── upstream/
├── .dockerignore
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── pyproject.toml
├── README.md
├── setup.py
└── uv.lock
```
