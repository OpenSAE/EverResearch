# MathVista environment

## Purpose and main function

Set up Python and locate the datasets and services used for MathVista evaluation.

## Scope of application

Use these steps from a MathVista checkout with Python 3.11 or newer.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Set `MATHVISTA_PROJECT_ROOT` to the copied template's path when using an
installed package from outside the project.

The generation and scoring commands use the
[official MathVista dataset](https://huggingface.co/datasets/AI4Math/MathVista) by
default. Optional local JSON files live under `../data/math_vista/upstream`.
Set `MATHVISTA_DATA_ROOT` to override that directory. To copy the original JSON files from a separate MathVista upstream checkout,
set `MATHVISTA_UPSTREAM` to that checkout with revision `24b1478` available:

```sh
mkdir -p ../data/math_vista/upstream
git -C "$MATHVISTA_UPSTREAM" archive 24b1478 data | tar -x -C ../data/math_vista/upstream --strip-components=1 --exclude='data/texts'
```

Local image generation also needs the official images ZIP unpacked below the data
root. The `testmini` split contains public answers. Scoring the `test` split
requires private labels from the dataset owners.

Azure generation and model-assisted extraction use
`AZURE_OPENAI_API_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`,
and `AZURE_OPENAI_MODEL`. The historical Claude and Bard adapters need the
optional `anthropic` or `bardapi` package and use `ANTHROPIC_API_KEY` or
`_BARD_API_KEY`, respectively. Service access is required to verify those
adapters live. The optional vision captioning and text recognition utilities need
`torch` and `transformers`, or `easyocr`, respectively.

## Local Qwen weights

Install MathVista with `python -m pip install -e '.[qwen]'` in a Python environment
with a CUDA build of PyTorch for the target GPU. The local model uses
Qwen2.5-VL-3B-Instruct safetensors. Set `MATHVISTA_QWEN_WEIGHTS` to the
downloaded directory or pass `--model_path`. The model loads the checkpoint
in place with network weight downloads disabled.
[Official checkpoint revision](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/tree/66285546d2b821cf421d4f5eb2576359d3770cd3)

Activate the environment with the Qwen extra installed and set the local weight
directory. Use this same interpreter for all three stages.

```sh
export MATHVISTA_QWEN_WEIGHTS=/path/to/Qwen2.5-VL-3B-Instruct
qwen_python=python
mathvista_python=python
```

This run used Python 3.12.15, PyTorch 2.11.0+cu128, Transformers 5.22.2 and
an NVIDIA RTX 5090 with 32 GiB of VRAM. Qwen uses BF16 on CUDA.
