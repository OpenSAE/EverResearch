# Reasoning Gym maintenance and acceptance

## Purpose and main function

Record the source locations, maintained entry points, and verification for the Reasoning Gym checkout connected to EverResearch.

## Scope of application

Use this record when working from the adopted baseline at upstream revision `5aea50d`. The public Python name remains `reasoning_gym`. Install the checkout before running the task commands.

Source snapshot [open-thought/reasoning-gym at 5aea50d](https://github.com/open-thought/reasoning-gym/tree/5aea50d292a6427f12c63c77873ec8ae945cd2c0).

Run `python -IS .everresearch/maintain.py check` from the copied project.
Follow the [environment guide](environment/README.md) and [formal run choices](experiment.md)
to reproduce the bounded checks or scale to the documented workloads.


| Workflow | Implementation before adoption | Current implementation and entry |
| --- | --- | --- |
| Dataset generation and scoring | `reasoning_gym/` | `datasets/` contains generator families and inputs access. `base/reasoning_gym/` provides the public API, registry, coaching, and shared scoring. Start with `reasoning_gym.create_dataset`. |
| Command client and server | `tools/` | `base/tools/`. Use `rgc` or `uvicorn tools.server.server:app`. |
| Remote evaluation | `eval/` | `tasks/evaluation/` and `models/remote_api/`. Use `python main.py evaluate --config <recipe>`. Use `python main.py precheck --config <recipe>` for an endpoint check, or add `--datasets-only` to check the data alone. |
| Local evaluation and GRPO training | `training/` | `tasks/local_evaluation/` and `tasks/training/`, model adapters under `models/`, and the training dataset adapter under `datasets/training_rows/`. See the [training guide](../tasks/training/README.md) for checkpoint, framework, and recipe requirements. |
| Examples and historical analyses | `examples/`, `notebooks/`, `scripts/` | `scripts/examples/`, `scripts/notebooks/`, and `scripts/`. Associated generator inputs and paper recipes are under `assets/`. |

Strict project layout and core dependency checks passed. The regression suite passed all 804 tests. An isolated installation of the built wheel created and scored one fixed-seed sample from each of the 106 registered datasets. Six selected records and scores matched the original checkout. The wheel also exposed the existing `rgc` command and server import.

The [runtime profiles](experiment.md) cover the remote evaluator against a local service with official weights, the local Transformers backend, and single-device GRPO on CUDA. All three recorded an automatic precheck and a measured workload. The configuration, manifest, and products are stored together under each descriptive study directory.

Use `python main.py read-run <directory>` for saved runs and `--resume <directory>` for remote checkpoints. Existing flat evaluation results remain readable.
