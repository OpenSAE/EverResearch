# LightEval documentation

[Execution environment](environment/README.md) covers installation, resources, and how to check which environment a run used.

Start with the [Quick Tour](code/evaluation/source/quicktour.mdx) for a runnable evaluation. The [repository guide](code/evaluation/source/development/project-structure.mdx) follows the command through registration, sample preparation, model inference and result writing.

| Location | What to look up |
| --- | --- |
| `base/` | Command dispatch, evaluation orchestration, and result readers. [Runtime and entry points](base.md) |
| `datasets/` | Hub dataset loading, split selection, and batching for inference. [Evaluation data](datasets.md) |
| `models/` | Backend selection, model construction, and model input and output interfaces. [Model adapters](models.md) |
| `tasks/` | Benchmark definitions, prompting, metrics, a chance baseline, and evaluation prechecks. [Evaluation tasks](tasks.md) |
| `conf/` | [Component names for local studies](conf.md) and their relation to public task and model IDs. |
| `experiment/` | [Saved scores, response replay and historical evidence](experiment.md). |
| `scripts/examples/` | Runnable custom model and task examples, backend YAML inputs and Nanotron inputs. |
| `tests/` | Product checks, optional integration checks and fixtures. Run `python -m pytest` from the checkout. |
| `assets/` | Benchmark task lists, original reproducibility logs, and the project logo. |
| `doc/code/evaluation/source/` | User guides and public API reference, built from `_toctree.yml`. |
| [Maintenance record](maintenance.md) | Changes to the checkout layout and verification of the installed package. |
