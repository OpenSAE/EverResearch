# Classification experiment records

## Purpose

Describe how to locate and read the results of each classification execution.

## Scope

Use this page after running precheck, training, or a performance comparison in
the copied CUB project.

Start with the run directory printed by the command, then use
`python -m cub_template inspect <run-directory>` to read its manifest.
The directory contains the effective `config.yaml`, `metadata/manifest.json`,
and the reports and artifacts listed in the manifest. The execution name is
readable and the manifest stores the unique identifier and timestamps.

Use the [offline exercise](../README.md#offline-exercise) for a bounded CPU run
on synthetic inputs. To reproduce earlier settings, supply the saved config with
`--config` and a descriptive `--subname`. Compare results using the recorded
configuration and inputs.
