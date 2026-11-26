# Supervised fine-tuning configuration

## Purpose and main function

Configure the supervised fine-tuning experiment around TRL's existing dataset selection and training implementation.

## Scope of application

`main.py` reads `conf/config.toml` by default. Pass `--config` to read another recipe. The ordinary installed `trl` command reads its own options and configuration.

`[recipes]` selects an installed training command, a named Zen dataset configuration, batch size, and task parameters. With no `--task`, the maintained launcher selects SFT. The `[benchmark]` values set the pinned dataset revision, workload counts, ten-row target, time budget, and reward checkpoint. The `[model]` section pins the trainable and local teacher checkpoint.

Formal runs train one epoch and evaluate the official test split. `--max-steps` limits only the formal training phase. The gate always runs before it and writes its own command and timing evidence. Older standalone recipe files without `[recipes]` use the historical SFT invocation.
