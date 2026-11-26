# CogVideoX project guide

## Purpose and main function

This guide connects the public commands to the models, conditioning inputs, and experiment records used by CogVideoX.

## Scope of application

Use it to install or verify the checkout, generate videos, fine-tune a model, or locate the retained SAT and utility workflows.

| Guide | What it covers |
| --- | --- |
| [Environment](environment/README.md) | Python, CUDA, optional tool dependencies, and a precheck |
| [Inference settings](conf.md) | Input modes, model cases and settings precedence |
| [Generation results](experiment/README.md) | The saved video, effective settings, and how to read a run |
| [Formal run choices](experiment/formal_runs.md) | Complete generation, fine-tuning and video-processing workloads with timing evidence |
| [Diffusers fine-tuning](code/diffusers_finetuning/README.md) | Training manifests, distributed launch, LoRA and full fine-tuning |
| [SAT workflows](code/sat_workflows/README.md) | SAT checkpoints, model and run overlays, sampling and training |
| [Composite web demo](../scripts/composite_demo/README.md) | Gradio demo, interpolation and super-resolution |
| [Caption examples](code/caption/README.md) | CogVLM2 video captioning |
| [Video enhancement](code/video_enhancement/README.md) | Upstream VEnhancer setup and use |

The main generation entry point lives in `base/cogvideo_runtime/`. Its media reader, model loading code, generation task, and precheck live in `datasets/video_input/`, `models/cogvideo_generation/`, `tasks/video_generation/`, and `tasks/precheck/`.

Run `python -IS .everresearch/maintain.py status` from the checkout to locate the active maintenance guide.

- [Maintenance and formal run choices](maintenance.md) records ownership, validation evidence, and run conditions.
