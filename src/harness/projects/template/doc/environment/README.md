# Implementation environment

## Purpose

A methodology for preparing, selecting and confirming the environment in which this classification projects are implemented.

## Scope

For local offline exercises, CUB official running and historical environmental review.

- Use Python 3.11 or more, relying on the version to bind to [install configuration](../../pyproject.toml). Install `python -m pip install -e .` with the selected interpreter.
- Offline prechecks can be used for CPUs and `synthetic`, and official CUB operations require local depressure data. The device selection and input path are available [parameter](../conf.md) (for configuration files, default values and overlay rules, see default values and effects of `training.batch_size`) and the actual running command is available [on the first page of the project](../../README.md) (checking existing functions and normal commands from the project entry, for example by looking at directly usable workflows).
- The `environment` operating list records the actual interpreter, Python and the main dependent version, equipment and operating conditions. Fields are from [Environmental collection](../../base/cub_template/runtime/environment.py).
