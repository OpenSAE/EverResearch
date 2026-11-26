# NanoChat maintenance

## Purpose and main function

Describe the upstream source, supported workflows, and verification for this template.

## Scope of application

Use this guide after copying the template to install dependencies, check the structure, or choose a real research workload.

Source snapshot [karpathy/nanochat at 92d63d4](https://github.com/karpathy/nanochat/tree/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd).

ClimbMix loaders, tokenization, decoder models, and training and evaluation commands. The verified workflows include real tokenizer training, CPU pretraining and checkpoint readback, supervised and reinforcement learning, and GPU inference.

1. Follow the [environment guide](environment/README.md) to install the project and prepare inputs.
2. Run `python -IS .everresearch/maintain.py check` from the copied project root.
3. See the [run and verification guide](experiment.md) for commands, recorded evidence, and requirements.
