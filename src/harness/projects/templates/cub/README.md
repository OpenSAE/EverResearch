# BirdStudy

## Purpose and main function

BirdStudy shows how to organize a research project around a CUB-200 bird classification task. It connects a dataset, a model, and the task to a public command that records its effective configuration and results.

## Scope of application

Use the project as a reference for setup, prechecks, and reproducible experiments. The structure check needs only Python. Training and the synthetic exercise require the dependencies declared in pyproject.toml, including PyTorch, torchvision, and Hydra.

## Check the project structure

From this directory, run the bundled offline checker:

```sh
python -IS .researchharness/maintain.py check
```

With EverResearch installed, run the full structure check:

```sh
rh projects project check . --json
```

## Explore the project

| Path | Responsibility |
| --- | --- |
| base/cub_template/ | CLI, component selection, prechecks, and run records |
| datasets/ | CUB-200 loading and synthetic samples |
| models/ | ResNet and convolutional model variants |
| tasks/ | Classification, evaluation, and a separate precheck |
| conf/config.yaml | Default dataset, model, task, and runtime settings |
| doc/ | Project, configuration, results, and environment guides |
| experiment/ | Effective configurations, manifests, reports, and model weights |

See the [project documentation](doc/README.md) and the [layout example](doc/code/development/layout.md) for the actual entry points and responsibilities.

## Run a small synthetic experiment

Install the project and its dependencies in an active Python environment:

```sh
python -m pip install .
```

To keep Python build files out of the project being checked, run the installation in a disposable copy of BirdStudy. Run the precheck and a small CPU run from the original project root. Both commands use synthetic samples.

```sh
python -m cub_template precheck --subname offline_check --set dataset=synthetic --set model=resnet18_mlp_small --set runtime.device=cpu --set runtime.workers=0 --set benchmark.samples=4
python -m cub_template run --subname offline_check --set dataset=synthetic --set model=resnet18_mlp_small --set runtime.device=cpu --set runtime.workers=0 --set training.batch_size=2 --set training.epochs=1
```

To compare data-loader performance, run `python -m cub_template benchmark` with the same options and add `--candidate-workers 1`.

Each command reports the run directory. Use `python -m cub_template inspect <run-directory>` to read its manifest and results. The run saves the effective configuration in `config.yaml`, result metadata in `metadata/manifest.json`, and training outputs under `reports/` and `artifacts/`. Use the saved configuration with `--config` and a new `--subname` to rerun an experiment.

## Use CUB-200 data

Download [Caltech-UCSD Birds-200-2011](https://www.vision.caltech.edu/datasets/cub_200_2011/) and point `--data-root` to the extracted directory containing `images/`, `images.txt`, `image_class_labels.txt`, and `train_test_split.txt`. The default model starts with random weights.

```sh
python -m cub_template precheck --subname scratch_baseline --data-root /path/to/CUB_200_2011
python -m cub_template run --subname scratch_baseline --data-root /path/to/CUB_200_2011
```

## Connect to EverResearch

BirdStudy starts in offline maintenance mode. To use shared guidance and local resource bindings, register the project and switch it to online maintenance:

```sh
rh projects register cub --path .
rh projects setup-maintenance . --online
python -IS .researchharness/maintain.py status
```
