# CogVideoX environment

## Purpose and main function

Set up Python and the dependencies for the installed CogVideoX commands and optional examples.

## Scope of application

Use these commands from the repository root in an isolated Python 3.10 to 3.12 environment. The project can use an existing CUDA-compatible PyTorch installation.

```sh
python -m pip install .
cogvideo precheck --prompt "A girl riding a bike."
cogvideo-finetune --help
```

Use a Python environment with the shared EverResearch dependencies for the online structure check.

```sh
python -IS .everresearch/maintain.py check
```

The precheck reports the resolved model, input mode, resolution and missing core Python packages. A generation run needs a CUDA GPU and the selected model weights. Give `--model_path` a Hugging Face model ID or a local checkpoint directory with the same model basename. Hugging Face downloads use the user’s configured cache. Image-to-video and video-to-video also need a media file or URL.

The [Diffusers fine-tuning guide](../code/diffusers_finetuning/README.md) covers datasets and GPU requirements. Install `requirements_sat.txt` for the SAT workflows, `requirements_composite.txt` for the composite Gradio demo, and `requirements_caption.txt` for captioning. The [root requirements file](../../requirements.txt) covers the wider upstream inference demonstrations.

From another working directory, installed commands use the current directory for relative inputs. Pass `--workspace /path/to/CogVideoStrictAdoption` to place managed generation records in this checkout.
