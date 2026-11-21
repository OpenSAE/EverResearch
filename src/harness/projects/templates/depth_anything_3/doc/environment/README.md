# Installation and runtime environment

Install the checkout with `python -m pip install -e .` in an environment meeting
the Python and dependency declarations in [pyproject.toml](../../pyproject.toml).
Install `.[app]` for Gradio or `.[gs]` for Gaussian rendering. Streaming uses
[additional dependencies and weights](../code/guides/streaming.md). The main
CLI defaults to CUDA. Supply `--device cpu` for a supported CPU inference setup.
Inference needs an input sequence and the selected local or Hugging Face
checkpoint. Benchmark datasets must be prepared as described in the
[benchmark guide](../code/guides/benchmark.md).

Run `python -m pytest -q` for local tests and
`da3 auto assets/examples/SOH --experiment scene_geometry --show-config`
to check input detection, configuration and output planning without loading weights.
Saved inference results identify the actual Python interpreter and version in
their execution manifests. The preserved SOH reports include the original
dependency, accelerator, revision and checkpoint checksums.

## Streaming dependency

For streaming loop detection, install the project’s SALAD dependency under `third_party/salad` from [the upstream SALAD repository](https://github.com/serizba/salad/tree/6aede13a3f6c25750bf7fde10209c06cb73060bb).
