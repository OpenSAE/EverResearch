# Evaluation inputs and configuration

Use `lighteval accelerate --help` for the complete set of CLI parameters. The backend accepts a comma-separated model configuration or a YAML file with `model_parameters` and optional `metric_options`. Explicit CLI options such as `--max-samples` affect the current run. The execution's `config.json` records the effective model and task settings.

## `conf/config.yaml`

The result tracker reads `catalogs.dataset`, `catalogs.model`, and `catalogs.task` when locating a local study. Each entry maps the directory name to a public identifier. For example, the dataset mapping `truthful_qa: truthfulqa/truthful_qa` gives that Hub dataset the directory name `truthful_qa`. The same naming rules apply when the tracker saves or reopens a study. The selected dataset, model, and task come from the CLI or Python API. [Study catalog](../conf/config.yaml)

Example model configuration files for the different backends are in [scripts/examples/model_configs](../scripts/examples/model_configs).
