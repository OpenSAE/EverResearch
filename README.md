<div align="center">

# EverResearch

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ever-research?label=PyPI&logo=python&logoColor=white)](https://pypi.org/project/ever-research/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compatible-blue)](plugins/agent-plugin/)
[![Skills.sh](https://img.shields.io/badge/Skills.sh-15%20skills-171717?logo=vercel&logoColor=white)](https://skills.sh/opensae/everresearch)
[![Checks](https://github.com/OpenSAE/EverResearch/actions/workflows/install-smoke.yml/badge.svg)](https://github.com/OpenSAE/EverResearch/actions/workflows/install-smoke.yml)
[![npm installer](https://img.shields.io/badge/npm-Installer-CB3837?logo=npm&logoColor=white)](plugins/installer/)

[中文](README.zh-CN.md)

</div>

EverResearch gives your AI agent the tools to understand and maintain a research project. It maps how datasets, models, and code fit together, runs project checks, and connects experiments to their configurations and results so you can reproduce past work and build on it. It works with your existing project files, Python environments, and compute.

## See it in action

![Terminal demo showing a read-only onboarding report, the organized project, and two matching experiment results](src/harness/utils/release/assets/quick-demo.gif)

Once installed, run `rh utils quick-demo ./QuickDemo`. The demo creates a sample project, previews its organization, and runs two experiments in a prepared organized copy. It reproduces the first run from its saved configuration and compares the metrics. The sample needs only Python and synthetic data.

EverResearch can also map how a paper or codebase fits together. Open the [interactive paper map](https://atheavenma.github.io/ExtractStructure/examples/attention-is-all-you-need-paper-structure.html) to trace the components and their connections.

[![An interactive structure map of Attention Is All You Need](.agents/skills/extract-structure/assets/screenshots/attention-paper-structure.png)](https://atheavenma.github.io/ExtractStructure/examples/attention-is-all-you-need-paper-structure.html)

<a id="install"></a>

## Quick Start

**Terminal.** Install the current GitHub build with Python 3.11–3.13 and try the demo. For the latest packaged release, use `uv tool install ever-research`.

```bash
uv tool install --from git+https://github.com/OpenSAE/EverResearch.git ever-research
rh doctor
rh utils quick-demo ./QuickDemo
```

**Codex.** Install the plugin, then open your research project.

```bash
codex plugin marketplace add OpenSAE/EverResearch
codex plugin add ever-research@ever-research
```

**Other agents.** Install the portable skills in your research project with [Skills CLI](https://skills.sh/opensae/everresearch).

```bash
npx --yes skills add https://github.com/OpenSAE/EverResearch/tree/main/plugins/agent-plugin --all -y
```

<details>
<summary><b>Platform guides and other installation options</b></summary>

| Agent | Installation |
| --- | --- |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/codex-color.svg" alt="" width="18" height="18"> Codex | [Codex plugin](plugins/codex-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/claude-color.svg" alt="" width="18" height="18"> Claude Code, Claude Cowork and web | [Claude plugin](plugins/claude-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/cursor.svg" alt="" width="18" height="18"> Cursor | [Cursor plugin](plugins/cursor-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/githubcopilot.svg" alt="" width="18" height="18"> GitHub Copilot CLI | [Agent Plugin](plugins/agent-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/gemini-color.svg" alt="" width="18" height="18"> Gemini CLI | [Gemini extension](plugins/gemini-extension/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/qwen-color.svg" alt="" width="18" height="18"> Qwen Code | [Agent Plugin](plugins/agent-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/deepseek-color.svg" alt="" width="18" height="18"> DeepSeek Harness | [DeepSeek plugin](plugins/deepseek/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/opencode.svg" alt="" width="18" height="18"> OpenCode | [OpenCode plugin](plugins/opencode/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/openclaw-color.svg" alt="" width="18" height="18"> OpenClaw | [OpenClaw plugin](plugins/openclaw/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/vercel.svg" alt="" width="18" height="18"> Skills CLI | [Skills.sh](https://skills.sh/opensae/everresearch) |
| Other agents | [Portable Skills](plugins/agent-plugin/) · [CLI and installer](plugins/installer/) |

Run the following inside Claude Code to add its native plugin.

```text
/plugin marketplace add OpenSAE/EverResearch
/plugin install ever-research@ever-research
```

Download the wheel, npm installer, or offline plugin ZIPs from [GitHub Releases](https://github.com/OpenSAE/EverResearch/releases/latest). See the [installer guide](plugins/installer/) for exact commands. To use the latest source checkout, run `python -m pip install .` there.

GitHub-installed skills download and verify a pinned EverResearch runtime on first use and cache it on the host. Offline plugin ZIPs include the runtime. For execution, the agent needs Python and access to your project and its dependencies.

</details>

### Three workflows to try

| Goal | Ask your agent | What you get |
| --- | --- | --- |
| Adopt an existing project | “Plan how to organize this repository with EverResearch. Identify current commands, data, configs, and results. Show proposed moves and verification steps, then wait for my approval.” | A file-by-file plan and the commands the agent will preserve. |
| Add a dataset or model | “Add this dataset or model to the current training task. Reuse the existing pipeline and show which configuration selects it.” | A reusable component, the configuration that selects it, and a check through the existing task. |
| Reproduce an experiment | “Reproduce the baseline from its recorded configuration. Save a separate run and compare the metrics and settings.” | A new experiment record and a comparison tied to both configurations. |

Run `rh projects project check ./MyProject --onboarding` for a read-only inventory and a prompt you can paste into your agent. This preview is the default for a project you have yet to configure. Use `--strict` to validate the structure, or `--json` for the original machine-readable check and pass/fail status.

Start on a new branch with a saved baseline. Ask the agent to preserve your existing entry commands, data, and results. Approve the proposed file changes before the agent applies them and explicitly approve any removal. Review the diff and run the existing commands before merging. The original branch keeps the baseline available if you want to abandon the changes.

## Features

Research is a continuous process. New experiments build on old results, models evolve, and research code needs to remain understandable to both humans and AI agents.

EverResearch helps you maintain that continuity across the research project.

| Capability&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | What you can do |
| --- | --- |
| **Project&nbsp;Management** | Start a new scientific project or reorganize existing research code around clear component responsibilities. |
| **Component&nbsp;Management** | Add datasets, preprocessing pipelines, model variants, and weights while keeping them reusable across experiments. |
| **Experiment&nbsp;Management** | Connect configurations, execution commands, results, and artifacts so previous experiments can be revisited. |
| **Code&nbsp;Maintenance** | Let your agent understand component relationships, make coordinated changes, and preserve working entry points. |
| **Structure&nbsp;Mapping** | Explore scientific papers and code repositories through interactive structure maps. |
| **Knowledge&nbsp;Management** | Organize reusable scientific knowledge, research notes, and insights for future work. |
| **GitHub&nbsp;Publishing** | Prepare project releases and publish updates to GitHub repositories. |
| **Hugging&nbsp;Face** | Download and publish datasets, and manage Spaces using your Hugging Face account. |

## How It Works

EverResearch gives your agent a shared understanding of how a scientific project is organized. Each component has a clear responsibility, allowing new datasets, models, and experiments to fit into the same project as research progresses.

```text
YourProject/
├── base/          # Shared code and execution entry points
├── datasets/      # Data loading and preprocessing
├── models/        # Model implementations and variants
├── tasks/         # Training, evaluation, and analysis
├── conf/          # Experiment configurations
├── experiment/    # Experiment records and results
├── scripts/       # Standalone utilities
├── tests/         # Project tests
└── doc/           # Research and project documentation
```

Start from scratch or bring an existing repository. EverResearch helps your agent understand the current project before reorganizing it, preserving useful code, supported commands, and existing results.

- **Before a run** review the effective configuration and run the project’s precheck.
- **After a run** keep the configuration and outputs with the experiment, then run `rh projects experiment check ./MyProject`.
- **During a weekly review** ask your agent which experiments ran and which configuration produced the best result on your chosen metric.
- **Before submission** rerun a key result from its recorded configuration and compare the outputs.

The project remains yours. Its scientific code, execution commands, configurations, and experimental results stay within the project. EverResearch provides the shared maintenance workflows and tools.

## Research Skills

The [`maintain-project`](.agents/skills/maintain-project/SKILL.md) skill coordinates research project maintenance. It directs the agent to specialized skills according to the task rather than asking the user to manage every component separately.

| Skill | Responsibility |
| --- | --- |
| [`maintain-project`](.agents/skills/maintain-project/SKILL.md) | Whole-project understanding and maintenance |
| [`maintain-dataset`](.agents/skills/maintain-dataset/SKILL.md) | Datasets, preprocessing, and data loading |
| [`maintain-model`](.agents/skills/maintain-model/SKILL.md) | Model implementations, variants, and weights |
| [`maintain-task`](.agents/skills/maintain-task/SKILL.md) | Training, evaluation, and scientific tasks |
| [`maintain-conf`](.agents/skills/maintain-conf/SKILL.md) | Configurations and experiment parameters |
| [`maintain-experiment`](.agents/skills/maintain-experiment/SKILL.md) | Experiment execution, records, and results |
| [`maintain-base`](.agents/skills/maintain-base/SKILL.md) | Shared code, resources, and execution workflows |
| [`maintain-code`](.agents/skills/maintain-code/SKILL.md) | Code dependencies and reusable implementations |
| [`maintain-knowledge`](.agents/skills/maintain-knowledge/SKILL.md) | Research knowledge and reusable insights |
| [`extract-structure`](.agents/skills/extract-structure/SKILL.md) | Interactive paper and code structure maps |
| [`maintain-github`](.agents/skills/maintain-github/SKILL.md) | GitHub project and release workflows |
| [`maintain-huggingface`](.agents/skills/maintain-huggingface/SKILL.md) | Hugging Face repositories, downloads, uploads, and Spaces |

See the [complete skill library](.agents/skills/) for additional maintenance workflows.

All agent integrations share the same research skills and core tools, so the way your projects are organized does not depend on a particular model or agent.

## Research Projects

EverResearch has applied its project organization approach to nine scientific project templates, covering computer vision, multimodal learning, retrieval, language model evaluation, and other machine learning tasks.

| Project | Research area |
| --- | --- |
| [CUB-200](src/harness/projects/templates/cub/) | Fine-grained image classification |
| [Depth Anything 3](src/harness/projects/templates/depth_anything_3/) | Depth estimation |
| [FastVLM](src/harness/projects/templates/fastvlm/) | Efficient vision-language modeling |
| [FlagEmbedding](src/harness/projects/templates/flag_embedding/) | Text embeddings and retrieval |
| [LightEval](src/harness/projects/templates/light_eval/) | Language model evaluation |
| [LLMLingua](src/harness/projects/templates/llmlingua/) | Prompt compression and LLM efficiency |
| [RF-DETR](src/harness/projects/templates/rf_detr/) | Object detection |
| [SAM2](src/harness/projects/templates/sam2/) | Image and video segmentation |
| [VGGT](src/harness/projects/templates/vggt/) | 3D visual geometry |

For a full training example, download BirdStudy from [GitHub Releases](https://github.com/OpenSAE/EverResearch/releases/latest) or browse its [CUB-200 template](src/harness/projects/templates/cub/).

<details>
<summary><b>SAM2 before and after</b></summary>

Selected top-level paths from [upstream SAM2](https://github.com/facebookresearch/sam2) and the [organized template](src/harness/projects/templates/sam2/).

```text
Upstream SAM2           EverResearch SAM2 template
sam2/                   base/         Shared runtime and launchers
training/               conf/         Task and model settings
sav_dataset/            datasets/     Dataset adapters
checkpoints/            models/       Segmentation models
tools/                  tasks/        Training and inference
notebooks/              scripts/      Standalone tools
                        third_party/  Upstream implementation
```

</details>

## Roadmap

- Compare past experiment results alongside the settings that produced them.
- Improve the onboarding report using examples from more research repositories.
- Verify installation as agent hosts change their plugin interfaces.

Tell us which workflow would help your lab in [GitHub Issues](https://github.com/OpenSAE/EverResearch/issues).

## Documentation and Contributing

- [Contributing](CONTRIBUTING.md), [changes](CHANGELOG.md), and [software citation](CITATION.cff)
- [Agent plugins and installation](plugins/)
- [Research project organization and workflows](src/harness/projects/README.md)
- [CLI, npm installer and local usage](plugins/installer/)
- [Build from source and optional MCP integration](src/harness/utils/release/README.md)

We welcome contributions from researchers and developers. Share a research workflow, propose a reusable skill, or help bring EverResearch to another agent ecosystem through [GitHub Issues](https://github.com/OpenSAE/EverResearch/issues) and pull requests.

## License

EverResearch is released under the [Apache 2.0 License](LICENSE). Included third-party components retain their respective licenses.
