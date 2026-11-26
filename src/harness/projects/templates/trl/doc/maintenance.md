# TRL source ownership and acceptance

## Purpose and main function

Identify the implementation behind the installed TRL commands and record which adoption checks have run.

## Scope of application

This covers the checkout at upstream commit `23721a1` and its local EverResearch adoption.

Source snapshot [huggingface/trl at 23721a1](https://github.com/huggingface/trl/tree/23721a1a706fa04254f1bf6a68ee2482599a0b97).

After copying the template, follow the [environment guide](environment/README.md)
and run `python -IS .everresearch/maintain.py check`. Use the [stable training
recipes](experiment.md) and [additional public workflows](tasks.md) to check
real inputs and choose a complete workload. Cache the pinned models and data
before timing if you want to compare against the recorded CPU estimates.


| Responsibility | Location |
| --- | --- |
| Installed Python entry and shared command dispatch | `base/transformers_reinforcement_learning/` |
| Dataset formatting and packing | `datasets/preparation/` |
| Model construction helpers and activation adapters | `models/adapters/` |
| Stable trainers, configuration classes, and callbacks | `tasks/training/` and `tasks/configuration/` |
| Experimental trainers and supporting task code | `tasks/experimental/`, `tasks/experimental_parameters/`, `tasks/rewards/`, and `tasks/kernels/` |
| Official examples, regression fixtures, and reference docs | `scripts/examples/`, `tests/`, and `doc/code/reference/source/` |
| Configuration for the supervised acceptance recipe | `conf/config.toml` |
| Chat templates, reporting templates, and Accelerate presets | `assets/templates/` and `assets/configuration/` |

The installed distribution continues to use the `trl` package and command. Setuptools maps the existing imports to the relocated source. A one-step `trl sft` baseline and post-migration run used the same Zen split and tiny Qwen2 checkpoint. Both reported training loss 11.93 and 45 tokens and wrote a checkpoint. The standalone supervised precheck read one actual sample and returned finite loss.

## Verification on the current machine

The strict project layout passed without violations. The source distribution and wheel built successfully, and a fresh wheel install opened the public trainer imports and all expected resource groups. Pytest collected 4,843 tests. Focused command routing and parsing checks ran independently of GPU training.

The established training commands below each saved a model after one CPU optimizer step. The checks used the original Zen dataset configurations and the tiny Qwen2 checkpoint. GRPO and RLOO loaded the pinned tiny Qwen2 classification reward model as well.

| Installed command | Zen dataset configuration | Elapsed time |
| --- | --- | --- |
| `trl sft` | `conversational_language_modeling` | 9.7 s |
| `trl dpo` | `standard_preference` | 12.1 s |
| `trl reward` | `standard_implicit_prompt_preference` | 12.3 s |
| `trl kto` | `standard_unpaired_preference` | 12.6 s |
| `trl distillation` | `standard_prompt_only` | 12.1 s |
| `trl grpo` | `standard_prompt_only` | 9.7 s |
| `trl rloo` | `standard_prompt_only` | 9.9 s |

The earlier SFT adoption results provide the one-step parity reference. The current maintained recipes cover all seven installed training commands with a ten-unit startup gate, two official validation rows, checkpoint readback, and an invalid-split rejection per command. The later measurements and full-epoch estimates are in [training run choices](experiment.md). Python-only trainers and unavailable runtime paths are documented in [additional public workflows](tasks.md).
