# AgentFlow template instructions

## Purpose and main function

Locate the maintenance commands, original AgentFlow source, and organized template layout.

## Scope of application

Use these instructions when maintaining a copy of this AgentFlow template.

<!-- everresearch:search -->
## Locate projects and files

Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.
<!-- /everresearch:search -->

<!-- everresearch:mode -->
## Maintain this checkout

For a maintenance request, including read-only planning, **open this project's maintenance guide and the matching skill before reading project files or choosing a general-purpose skill**. The user's intended change determines the route. A missing configuration, run record, or implementation is something to investigate after reading the skill.

1. From the project root, run `python -IS .everresearch/maintain.py status`. This read-only command reports the mode and the guide path. Open the reported central guide in online mode or the [offline guide](.everresearch/offline/operations.md) in offline mode.
2. Use the guide's task table to choose and open the corresponding `SKILL.md`. For a request to read instructions, stop after reading the relevant guidance and reporting the files.

For a walkthrough or diagram of this codebase, use the guide's `extract-structure` entry to analyze the source and its relationships. Presentation tools can render that analysis after the source walkthrough. For a change to a reusable setting or default, use `maintain-conf`. For reproducing a run or reading its results, use `maintain-experiment`, including when you still need to locate the earlier run.

If `.everresearch/mode.toml` is missing and the user authorized EverResearch setup, run `rh projects setup-maintenance . --online` for online maintenance or `rh projects setup-maintenance .` for a standalone checkout. An older `mode.json` needs a current mode selection. If status reports a connection or mode error, report it before work that needs the guide. Use the user's selected mode.

For an authorized structure check, run `python -IS .everresearch/maintain.py check` from the project root. Use the project's own entry points to install, run tasks, and read their results.
<!-- /everresearch:mode -->

## Original project and template layout

- **Original project** [AgentFlow](https://github.com/lupantech/AgentFlow)
- **Source revision** [`b94006436b87`](https://github.com/lupantech/AgentFlow/tree/b94006436b8712ab8682846fb0d886a5f174f2d4)
- **Paper** [In-the-Flow Agentic System Optimization for Effective Planning and Tool Use](https://openreview.net/forum?id=Mf5AleTUVK) · ICLR 2026 Oral
- **Authors** Zhuofeng Li, Haoxiang Zhang, Seungju Han, Sheng Liu, Jianwen Xie, Yu Zhang, Yejin Choi, James Zou, Pan Lu
- **Original source archive** [AgentFlow-b9400643.zip](third_party/upstream/AgentFlow-b9400643.zip)
- **Archive SHA-256** `117e853c9c546be2081df46b5d0cfc0c96b7fd72ea9be1a6cd87a29278aedbb9`

### Before organization

```text
AgentFlow/
├── .gitignore
├── LICENSE
├── README.md
├── agentflow/
│   ├── .env.template
│   ├── .gitignore
│   ├── __init__.py
│   ├── agentflow/
│   ├── cli/
│   ├── client.py
│   ├── config.py
│   ├── instrumentation/
│   ├── litagent.py
│   ├── logging.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── reward.py
│   ├── runner.py
│   ├── scripts/
│   ├── server.py
│   ├── tracer/
│   ├── trainer.py
│   ├── types.py
│   └── verl/
├── assets/
│   ├── doc/
│   └── img/
├── data/
│   ├── aime24_data.py
│   └── get_train_data.py
├── pyproject.toml
├── quick_start.py
├── scripts/
│   ├── restart_ray.sh
│   ├── serve_vllm.sh
│   └── setup_stable_gpu.sh
├── setup.sh
├── test/
│   ├── 2wiki/
│   ├── aime24/
│   ├── amc23/
│   ├── bamboogle/
│   ├── calculate_score_unified.py
│   ├── gaia/
│   ├── gameof24/
│   ├── gpqa/
│   ├── hotpotqa/
│   ├── medqa/
│   ├── musique/
│   ├── solve.py
│   └── utils.py
├── train/
│   ├── config.yaml
│   ├── rollout.py
│   ├── rollout_dev.py
│   ├── serve_with_logs.sh
│   ├── train_agent.py
│   ├── train_with_logs.sh
│   └── utils.py
├── util/
│   ├── __init__.py
│   ├── get_pub_ip.py
│   ├── model_merger.py
│   ├── parse_config.py
│   ├── port_cleanup.py
│   └── upload_hf_model.py
└── uv.lock
```

### After organization

```text
agentflow/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitignore
├── AGENTS.md
├── LICENSE
├── README.md
├── assets/
│   ├── examples/
│   ├── images/
│   └── prepared_data/
├── base/
│   └── agent_flow/
├── conf/
│   ├── config.yaml
│   └── tasks/
├── datasets/
│   ├── benchmarks/
│   ├── preparation/
│   └── training/
├── doc/
│   ├── README.md
│   ├── code/
│   ├── environment/
│   ├── knowledge/
│   └── maintenance.md
├── models/
│   ├── components/
│   └── providers/
├── pyproject.toml
├── requirements.txt
├── scripts/
│   ├── benchmarks/
│   ├── diagnostics/
│   ├── examples/
│   ├── models/
│   ├── restart_ray.sh
│   ├── serve_vllm.sh
│   ├── setup/
│   ├── setup_stable_gpu.sh
│   └── training/
├── setup.py
├── tasks/
│   ├── benchmarks/
│   ├── inference/
│   ├── precheck/
│   └── training/
├── tests/
│   └── test_benchmark_precheck.py
├── third_party/
│   └── upstream/
└── uv.lock
```
