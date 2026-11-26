# LeRobot source ownership

## Purpose and main function

Locate LeRobot's original implementations in the adopted project and connect them to the commands that load them.

## Scope of application

Use this map to maintain the local LeRobot source snapshot, build it, or check an installed command. The snapshot identifies itself as LeRobot 0.7.1.

| Workflow or component | Original source group | Current source owner | Installed entry or package |
| --- | --- | --- | --- |
| Train a robot policy or reward model | `src/lerobot/scripts/lerobot_train.py` and tokenizer training | [Training](../../tasks/training/) | `lerobot-train`, `lerobot-train-tokenizer` |
| Evaluate a policy and serve policy inference | Evaluation and policy server scripts | [Evaluation](../../tasks/evaluation/) | `lerobot-eval`, `lerobot-policy-server` |
| Record, annotate, replay, and run a policy on a robot | Recording scripts and `src/lerobot/rollout/` | [Recording](../../tasks/recording/) and [rollout strategies](../../tasks/policy_rollout/) | `lerobot-record`, `lerobot-annotate`, `lerobot-replay`, `lerobot-rollout` |
| Train and deploy a reinforcement-learning policy | `src/lerobot/rl/` | [Reinforcement learning](../../tasks/reinforcement/) | `lerobot.rl` |
| Read, edit, and prepare demonstrations | `src/lerobot/datasets/`, data processing, and data scripts | [Datasets](../../datasets/) | `lerobot.datasets`, `lerobot.data_processing`, `lerobot.streaming`, `lerobot.transforms`, `lerobot-edit-dataset` |
| Select policies and load their weights | `src/lerobot/policies/`, `rewards/`, and `model/` | [Models](../../models/) | `lerobot.policies`, `lerobot.rewards`, `lerobot.model` |
| Run hardware, simulator, and shared processing code | Remaining libraries under `src/lerobot/` | [Shared library](../../base/lerobot_library/) | `lerobot-info`, `lerobot-env-server`, and published `lerobot.*` imports |
| Check training and evaluation configuration | Training configuration and evaluation command | [Prechecks](../../tasks/precheck/) | Runtime training and evaluation guards, plus `lerobot-precheck` for training configuration |
| Maintain build, tests, examples, and supporting material | `pyproject.toml`, `setup.py`, `tests/`, `examples/`, Dockerfiles, and docs | [Build mapping](../../conf/base/config.json), [tests](../../tests/), [examples](../../scripts/examples/), [container assets](../../assets/build/containers/), and [reference docs](reference/source/) | `uv build`, `uv run pytest tests`, and commands documented with each tool |

The [build mapping](../../conf/base/config.json) records the migrated sources whose installed names differ from their source paths. Both wheel and editable installations use it. The distribution keeps the original package names and includes the project-owned resources used at runtime. Optional dependencies remain declared in [the package configuration](../../pyproject.toml). The MolmoAct2 policy's vendored Hugging Face modeling files stay with the policy build under the original Python package namespace and retain their source headers.

The [environment guide](../environment/README.md) lists the setup and verification commands.
