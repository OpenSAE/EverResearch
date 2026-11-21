# Execution environment

## Purpose and scope

Prepare the local interpreter, checkpoints and indexed inputs for LLMLingua. Use experiment records to recover the conditions of a particular run.

## Installation and resources

- [setup.py](../../setup.py) declares Python 3.8 or newer and the package dependencies. From the checkout use `python -m pip install -e .` or `make install` with the selected interpreter. The batch workflow uses a Transformers checkpoint and tokenizer. Its default device is CUDA; `--device_map` selects the device mapping. Match the device and available memory to the checkpoint.
- A batch run needs an indexed JSON input and all files for the selected checkpoint. Read the local interpreter, MeetingBank and GSM8K bindings and checkpoint cache with `rh projects resources llmlingua`. Use explicit paths from other working directories. Add `--experiment-root` when an installed wheel cannot locate the checkout.
- The [paper reproduction guide](../../scripts/benchmark_reproduction/README.md) covers optional training, annotation and scoring dependencies. Classifier training needs the spaCy English model specified by the workflow. Service-backed workflows require access to the configured service and credentials in the execution environment.

## Quick verification and run evidence

Use `python -c "import sys, llmlingua; print(sys.executable, llmlingua.__file__)"` and `python -m llmlingua compress --help` to confirm the active environment and arguments without loading a checkpoint. For a saved batch use `python -m llmlingua show RUN_DIRECTORY` and consult its effective configuration, manifest and any reproduction notes. The [experiment index](../experiment.md) and [maintenance record](../maintenance.md) identify the saved real runs and the bounded offline checks.
