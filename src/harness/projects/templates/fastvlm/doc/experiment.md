# Image prompts

## Purpose and main functions

Describe how to create and read this project’s local run outputs.

## Scope

Use these commands after copying the template and configuring the inputs and model described in the [project README](../README.md).

Use `python main.py` with a local image and a compatible checkpoint. Each new run has a readable directory name such as `prediction_execution_one`. The manifest retains its timestamp and unique run ID. Use `python main.py --read-result <manifest>` to recover the recorded answer from an existing or new run.
