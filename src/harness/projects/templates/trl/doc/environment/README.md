# TRL environment

## Purpose and main function

Install the local TRL source and check that the command-line and training entry points use it.

## Scope of application

Use these steps for the maintained CPU recipe and ordinary TRL commands. Optional trainers may add hardware and package requirements.

TRL requires Python 3.11 or later. From the repository root, install the source into an isolated environment with `python -m pip install -e .` and check `trl env` and `trl sft --help`. The reference verification environment used PyTorch 2.10.0, Transformers 5.24.1, Datasets 5.2.0, and Accelerate 1.16.0.

Verify access to the Zen conversational dataset and the tiny Qwen2 checkpoint through `python main.py precheck --study initial_readiness`. Their Hugging Face cache is managed by the local client. This recipe runs on CPU by default. See [experiment commands and results](../experiment.md) for the full recipe and records.

The first run can download the small pinned weights and Zen data. Cache them before enabling Hugging Face offline mode.
