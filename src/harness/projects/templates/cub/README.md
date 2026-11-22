# CUB-200 Classification Reference Items

## Purpose

Trains ResNet18 plus MLP headers to do 200-type whole-chart classification on CUB-200-2011. As a reference item for ResearchHarness, displays how components are organized, run, performance checks, results delivered and functional changes are maintained.

## Scope

From ResearchHarness Source directory used, or will be the whole cub The directory is copied to a stand-alone workspace as the starting point for the new project. `PYTHONPATH=base` . The project uses local Python and PyTorch,Runs from the root directory. `python -m pip install -e .`,Can also run directly when there is a dependency `python -m cub_template`.Three components of the root directory are included in the pack `cub_template` Namespace to avoid being named like the environment Python Collision.

These commands can be used in an independent workspace. When you choose to access ResearchHarness, you can use it to synchronize skills, bind the CDer Python and the directory of data, and the results of the registration structure.

## Full Layout

```text
cub/
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

`datasets/`,`models/`,`tasks/` It is a mandatory catalogue, each maintaining the registration of components. and SAEBase Similarly, the normal entry configuration, the operating layer calculates and returns the structured results based on the configuration selected task. Prechecks can be selected independently and are called from the operational level before formal training. Runlist logs precheck, task results and product path.

The data root is specified by the formula or `--data-root`. Run the root is fixed to the project level 1 directory `experiment/` and is positioned from the root of the project. Normal running is saved by `<dataset>/<model>/<task>/<subname>/<run-id>/`. Use `--subname` to use one or three words for the experiment to describe the purpose, such as `scratch_baseline` or `imagenet_finetune`. Use the same name when running the same experiment again, and the program creates a separate running directory. The list of configuration or component selection failures is `unresolved/<subname>/`. The official result is located by `metadata/manifest.json`.

[Examples of template layouts](doc/code/development/layout.md)Description of what the directories are responsible for and when they are extended to be used in replicating templates, adding components and adjusting project layouts.

[Item documents](doc/README.md)Provide level I catalogue descriptions, use of parameters, experimental reports, scientific knowledge, implementation of environmental and source structure.

## Select Project Maintenance Mode

Item `AGENTS.md` Description of the basis `.researchharness/mode.toml` Select a maintenance source. The template defaults to shut down the central access and allows for the use of a handheld manual and a standard library check from an independent workspace. `python -IS .researchharness/maintain.py status` and `python -IS .researchharness/maintain.py check`.

To mount from the ResearchHarness that is available on this machine, the user sets `enabled` to `true`. The following commands are run on the project directory, starting directly with `apply` when already registered. Example by ResearchHarness in the project equivalent directory.

```bash
rh projects --harness-root ../ResearchHarness register cub --path .
rh projects --harness-root ../ResearchHarness apply cub
python -IS .researchharness/maintain.py status
```

Mount the generated online information at `.researchharness/online/`. The online mode fails to report when central is not available, switching to user-decided. The next section of the "offline exercise" refers to a scientific mission that runs with synthetic data and is independent of the project maintenance switch.

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

Prepare [Caltech-UCSD Birds-200-2011 official data](https://www.vision.caltech.edu/datasets/cub_200_2011/) to point `--data-root` to a decompression catalogue containing `images/`, `images.txt`, `image_class_labels.txt`, `train_test_split.txt`. Run the configuration to read only local data, starting with random weights. Officially divided between 5,994 training charts and 5,794 test charts.

```bash
python -m cub_template precheck --subname scratch_baseline --data-root "$cub_data"
python -m cub_template run --subname scratch_baseline --data-root "$cub_data"
```

The `cub_data` is first set as a directory of in-house data. The training is randomly calibrated and flipped. Formally tested for definitive scaling and central cutting.

## Results and follow-up

- `config.yaml` Saves a configuration that actually works.
- `metadata/manifest.json` Saves configuration references, data sources, software source documents, Hashi, measured environment, state and relative product paths.
- `reports/` Save-stage indicators, pre-checks, performance comparisons or final tests.
- `artifacts/model.pt` Saves the final model weight for this training.
- When data is missing, the list records specific missing items and restores them by `blocked`.

The project maintenance method is [examples of engineering work](doc/code/development/engineering.md). The project assistant first deals with conventional engineering issues on the basis of real documents and the results of the operation.
