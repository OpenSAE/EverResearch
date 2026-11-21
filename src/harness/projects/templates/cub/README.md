# CUB-200 Classification Reference Project

## Purpose

Train a ResNet-18 with a multilayer classifier head for 200-class image classification on CUB-200-2011. The template demonstrates component selection, prechecks, performance comparisons, and experiment records.

## Scope

Run the template in its source directory or copy it to a standalone workspace. Use Python and PyTorch, and run the examples from the project root. Install with `python -m pip install -e .`, or set `PYTHONPATH=base` if the dependencies are already installed. The package exposes its components under the `cub_template` namespace.

Use ResearchHarness to link shared skills, bind a local Python interpreter and data directory, and store structure maps when you attach this project to a workspace.

## Full Layout

```text
template/
├── README.md,AGENTS.md,pyproject.toml
├── datasets/
│   ├── plugins.py
│   └── cub200/
│       ├── __init__.py                   public entry point and support tasks
│       ├── dataset.py                    Description, image and official division
│       └── offline_samples.py            CUB Offline check input for classification
├── models/
│   ├── plugins.py,build.py               Registered from series, shared build
│   ├── resnet/resnet18/
│   │   ├── specs.py                      Two. ResNet18 + MLP Variables
│   │   └── model.py                      Achieving a common set of two variants
│   └── cnn/small_cnn/
│       ├── specs.py
│       └── model.py
├── tasks/
│   ├── plugins.py
│   ├── classification/
│   │   ├── task.py                        Mission interface, practical steps for precheck
│   │   └── operation.py                   Training, assessment and indicators
│   └── precheck/
│       ├── task.py                        Independent precheck and performance portal
│       ├── gate.py                        Formal Task Call Precheck
│       ├── timing.py                      Phase time
│       └── performance.py                 Baseline bottlenecks and candidate comparison
├── base/                                 Base Layer
│   └── cub_template/                      Command entrance and common running codes
│       ├── cli.py,__main__.py             Command entrance
│       ├── registry.py,contracts.py       Registration of queries, data and task results interface
│       └── runtime/
│           ├── config.py,environment.py   Configure Grouping, Operating Environment
│           ├── runner.py                  Selection of components, validation, precheck and distribution
│           └── records.py                 Run a list of identities, status and results
├── conf/
│   └── config.yaml                       Only Default Configuration
├── experiment/                           Fixed root of the experiment
│   └── <Data Set>/<Model>/<Tasks>/<subname>/<Run Identification>/
│       ├── config.yaml                    Entry into force configuration for single run
│       ├── metadata/manifest.json         State and product index
│       ├── reports/
│       └── artifacts/
├── tests/
│   ├── test_workflow.py                   Normal access and return of results
│   └── test_boundaries.py                 Configure quarantine, data disaggregation and candidate failure
└── doc/                            Project document index and table of contents at all levels
    ├── datasets.md,models.md,tasks.md,conf.md
    ├── experiment.md
    └── knowledge/,environment/,code/
```

`datasets/`,`models/`,`tasks/` It is a mandatory catalogue, each maintaining the registration of components. and SAEBase Similarly, the normal entry configuration, the operating layer calculates and returns the structured results based on the configuration selected tasks, the tasks defined and the results. Prechecks can be selected independently and are called from the operational level before formal training. Runlist records the prechecking check, the results of the task and the path of the product.

The data root is specified by the formula or `--data-root`. Run the root is fixed to the project level 1 directory `experiment/` and is positioned from the root of the project. Normal running is saved by `<dataset>/<model>/<task>/<subname>/<run-id>/`. Use `--subname` to use one or three words for the experiment to describe the purpose, such as `scratch_baseline` or `imagenet_finetune`. Use the same name when running the same experiment again, and the program creates a separate running directory. The list of configuration or component selection failures is `unresolved/<subname>/`. The official result is located by `metadata/manifest.json`.

[Examples of template layouts](doc/code/development/layout.md)Description of what the directories are responsible for and when they are extended to be used in replicating templates, adding components and adjusting project layouts.

[Item documents](doc/README.md)Provide level I catalogue descriptions, use of parameters, experimental reports, scientific knowledge, implementation of environmental and source structure.

## Skills portal maintained by the project

Open working session from the template directory, press `AGENTS.md` Selection `.agents/skills/` This template provides examples of operational components registration, independent precheck, performance comparisons, and results checks. Skills links that skip the template when copying to an independent workspace, are registered and the shared skills are opened and linked through the project access portal.

## Offline Exercise

Executes in the project directory. Runs to read the default value from `conf/config.yaml`, `--set` to select components or overwhelm parameters.

```bash
offline=(
  --subname offline_check
  --set dataset=synthetic --set model=resnet18_mlp_small
  --set runtime.device=cpu --set runtime.workers=0
  --set training.batch_size=2 --set training.epochs=1
  --set benchmark.samples=4
)
python -m cub_template precheck "${offline[@]}"
python -m cub_template run "${offline[@]}"
python -m cub_template benchmark "${offline[@]}" --candidate-workers 1
```

Read the previously saved configuration with `--config <run-directory>/config.yaml`. Run still needs to give `--subname` and generate a new running directory. Configure the source version of the list when reruning history experiments. Archived ImageNet fine tunes to its running copy.

The performance precheck report compares the number of current work processes and candidate values, showing the longest time-consuming phase of the baseline, consistency of results and recommended values. `--set runtime.workers=<Recommended value>` Runs, rechecks the actual workload with the total time. Each command prints a running directory. `python -m cub_template inspect <Run Directory>` Reads the active state and product path. The input for the offline formulation is marked `synthetic`,For validation of work process.

## Official CUB-200 baseline

Prepare [Caltech-UCSD Birds-200-2011 official data](https://www.vision.caltech.edu/datasets/cub_200_2011/) to point `--data-root` to a decompression catalogue containing `images/`, `images.txt`, `image_class_labels.txt`, `train_test_split.txt`. Run configuration only to read local data, with the model starting with a random weight. The official division is used to fix 5,994 training charts and 5,794 test charts.

```bash
python -m cub_template precheck --subname scratch_baseline --data-root "$cub_data"
python -m cub_template run --subname scratch_baseline --data-root "$cub_data"
```

The `cub_data` is first set as a directory of in-house data. The training is randomly calibrated and flipped. Formally tested for definitive scaling and central cutting.

## Results and follow-up

- `config.yaml` Saves a configuration that actually works.
- `metadata/manifest.json` Saves configuration references, data sources, software source documents, Hashi, measured environment, state and relative product paths.
- `reports/` Save-stage indicators, prechecks, performance comparisons or final tests.
- `artifacts/model.pt` Saves the final model weight for this training.
- When data is missing, the list records specific missing items and restores them by `blocked`.

The project maintenance method is [examples of engineering work](doc/code/development/engineering.md). The project assistant first deals with conventional engineering issues on the basis of real documents and the results of the operation.
