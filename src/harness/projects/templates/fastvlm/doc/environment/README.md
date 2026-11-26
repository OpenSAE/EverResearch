# Running and checking FastVLM

The published Python setup uses Python 3.10 with dependencies from `pyproject.toml`. Install from the source checkout with `pip install -e .`. The inferencer supports PyTorch MPS, CUDA and CPU. A model run records the selected device and library versions with its result. [Install instructions](../../README.md#setup) [Dependencies](../../pyproject.toml)

The Swift application requires the Apple platforms and Xcode described in its README. The Apple Silicon export requires Core ML tooling and the documented MLX-VLM checkout. [App requirements](../../third_party/apple_demo/README.md) [Export requirements](../code/apple_silicon/README.md)

Run the lightweight command, configuration and result checks from the source root.

```bash
python -m pip install pytest Pillow
python -m pytest -q
```

The tests use an image generated locally and stand-in inference components. They check defaults against the recipe and documentation, argument forwarding, input identity, result readback and checkpoint preservation. They require no published weights or live network services. The GitHub Actions workflow runs the same suite. [Test cases](../../tests/test_inference.py) [Workflow](../../.github/workflows/check.yml)

## CUDA on Blackwell

The project dependency pins select PyTorch 2.6.0 and torchvision 0.21.0. On the GeForce RTX 5090, the published checkpoint acceptance used the official PyTorch 2.7.1 and torchvision 0.22.1 wheels for CUDA 12.8. The override is local to the isolated environment. Run these commands from the project root. [PyTorch release notes](https://pytorch.org/blog/pytorch-2-7/) [Official wheel versions](https://pytorch.org/get-started/previous-versions/)

```bash
uv venv --python 3.10.22 --seed .venv
uv pip install --python .venv/bin/python \
  --override /dev/stdin --index https://download.pytorch.org/whl/cu128 -e . pytest <<'PINS'
torch==2.7.1+cu128
torchvision==0.22.1+cu128
PINS
```

The [published checkpoint acceptance](../experiment.md#published-checkpoint-acceptance) records the environment, package versions and inference results.
