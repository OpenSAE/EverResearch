<!-- everresearch:search -->
## Locate projects and files

Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.
<!-- /everresearch:search -->

<!-- everresearch:mode -->
## Choose the maintenance mode

### Purpose and main functions

Use the project setting to select its maintenance guide and structure checker.

### Scope

Use this section for project maintenance, checking the online connection, or running an offline structure check.

Start by reading `.everresearch/mode.toml`. Its `enabled` setting selects this project's maintenance mode. Follow the user's choice and obtain authorization before changing it.

- **`enabled = false` selects offline maintenance.** Use the project's [offline operations guide](.everresearch/offline/operations.md). It explains how to plan, carry out, and finish maintenance using the project's files, commands, tests, and data.
- **`enabled = true` selects online maintenance.** Run `python -IS .everresearch/maintain.py status` first. When it prints `online`, read the central guide at the reported path. Follow that guide to the operations manual, shared skills, and central checks in the EverResearch repository. If the status command fails, report the cause and pause work that requires central maintenance until the user restores the connection or selects offline mode.
- **A missing or invalid setting blocks maintenance.** Report the problem and continue once the setting has been corrected or the user has chosen a mode.

When a structure check is authorized, run `python -IS .everresearch/maintain.py check` from the project root. The command runs the checker for the selected mode. Follow the project README for installation, training, prechecks, and reading results.
<!-- /everresearch:mode -->

## Original project and template layout

- **Original project** [AI2 Safety Evaluation](https://github.com/allenai/safety-eval)
- **Source revision** [`060cc903d647`](https://github.com/allenai/safety-eval/tree/060cc903d64703214c549b5c3a30ea8ceef2e588)
- **Paper** [WildGuard: Open One-stop Moderation Tools for Safety Risks, Jailbreaks, and Refusals of LLMs](https://proceedings.neurips.cc/paper_files/paper/2024/hash/0f69b4b96a46f284b726fbd70f74fb3b-Abstract.html) · NeurIPS 2024 Datasets and Benchmarks Track · associated study
- **Authors** Seungju Han, Kavel Rao, Allyson Ettinger, Liwei Jiang, Bill Yuchen Lin, Nathan Lambert, Yejin Choi, Nouha Dziri
- **Original source archive** [ai2_safety_eval.zip](third_party/upstream/ai2_safety_eval.zip)
- **Archive SHA-256** `58cfb68477df2a59413ea518bf0eab0137a2fe38152dd68c7c7b705126ef584b`

### Before organization

```text
safety-eval/
├── Dockerfile
├── LICENSE.md
├── README.md
├── evaluation/
│   ├── __init__.py
│   ├── display_data_stats.py
│   ├── eval.py
│   ├── explore_data.py
│   ├── gantry_run.sh
│   ├── models/
│   ├── run_all_classification_benchmarks.py
│   ├── run_all_generation_benchmarks.py
│   ├── schemas.py
│   ├── tasks/
│   └── utils.py
├── requirements.txt
├── setup.py
└── src/
    ├── __init__.py
    ├── classifier_models/
    ├── data_utils.py
    ├── dispatch_openai_requests.py
    ├── generation_utils.py
    └── templates/
```

### After organization

```text
ai2_safety_eval/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitignore
├── AGENTS.md
├── LICENSE.md
├── README.md
├── assets/
│   ├── container/
│   └── source_data/
├── base/
│   ├── evaluation/
│   ├── evaluation_entry/
│   ├── evaluation_utilities/
│   └── shared_code/
├── conf/
│   ├── config.yaml
│   ├── models/
│   └── tasks/
├── datasets/
│   └── readers/
├── doc/
│   ├── README.md
│   ├── conf.md
│   ├── environment/
│   ├── experiment/
│   └── maintenance.md
├── models/
│   ├── classifier_models/
│   └── generators/
├── requirements.txt
├── scripts/
│   ├── gantry/
│   └── inspection/
├── setup.py
├── tasks/
│   ├── __init__.py
│   ├── classification/
│   ├── generation/
│   ├── metrics/
│   └── precheck/
├── tests/
│   └── product/
└── third_party/
    └── upstream/
        └── ai2_safety_eval.zip
```
