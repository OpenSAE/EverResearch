# Reasoning Gym environment

## Purpose and main function

Install the library and its optional dependencies and check which workflows the environment supports.

## Scope of application

The base library and its procedural dataset checks run on CPU with Python 3.10 or later. Remote evaluation also needs an OpenAI-compatible endpoint. Local evaluation can use CPU Transformers. Distributed training uses the GPU dependencies and checkpoints named in the [training guide](../../tasks/training/README.md).

Create an isolated Python environment and run these commands from the checkout root.

```sh
python -m pip install -e '.[test,server,cli,scoring]'
python -m pip install -r requirements_evaluation.txt
python main.py precheck --datasets-only
python -m pytest
rgc --help
```

The wheel installs the `reasoning_gym` library and the `rgc` command. The checkout exposes the task launcher and its recipes. The data-only precheck samples and scores the configured datasets without sending prompts to an external service. See the [deployment instructions](../code/tools.md) for the optional local server.


For local Transformers inference or the loopback evaluation endpoint, install
a compatible PyTorch build and `transformers[serving]` alongside the evaluation
dependencies. The recipes use `Qwen/Qwen2.5-0.5B-Instruct`. Cache the checkpoint
before timing, or point the model fields at a local snapshot.

Single-device GRPO requires a CUDA PyTorch build and a compatible TRL install in
the selected environment. The verified run used TRL 1.20.0.dev0 from the
companion template. See the [run guide](../experiment.md) for the smoke workflow.
