# DINOv2 environment

## Purpose and main function

Set up DINOv2 and verify that the local checkout can decode an image and produce features.

## Scope of application

Use these instructions from the project root for the source checkout or an independent
installation. See the upstream [installation notes](../../README.md#installation) for
the pinned PyTorch, torchvision and xFormers versions and dense prediction dependencies.

Install the dependencies in a compatible Python environment, then install the local package.

```sh
python -m pip install -r requirements.txt
python -m pip install --no-deps .
```

The [environment definitions](../../scripts/environment) provide the original Conda
environments for training, classification and optional dense tasks. Real distributed training
and evaluation also require the task's GPU, dataset files, checkpoint and scheduler environment
described in the [workflow examples](../../README.md#training).

From a checkout, use `python main.py --help` to list commands. To test a small CPU workflow,
run `XFORMERS_DISABLED=1 python main.py precheck`. It uses a generated image, the project decoder and transform,
and the untrained ViT-S/14 backbone. It prints the selected config and verifies a finite
384-dimensional feature vector. Pass `--image /path/to/image.png` to check a local image.

For installed use from any working directory, run commands such as
`python -m dinov2.run.eval.knn --help`. Local PyTorch Hub examples use
`third_party/pytorch_hub` under this checkout as the Hub directory and import the installed
`dinov2` package. The [maintenance check](../../AGENTS.md#choose-the-maintenance-mode)
verifies the project layout independently of the project runtime.

Use an isolated project interpreter. Reference timings used Python 3.12 with PyTorch 2.10 and CUDA 12.8 on one RTX 5090.
