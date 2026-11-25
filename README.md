<div align="center">

# EverResearch

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ever-research?label=PyPI&logo=python&logoColor=white)](https://pypi.org/project/ever-research/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compatible-blue)](plugins/agent-plugin/)
[![Skills.sh](https://img.shields.io/badge/Skills.sh-15%20skills-171717?logo=vercel&logoColor=white)](https://skills.sh/opensae/everresearch)
[![npm installer](https://img.shields.io/badge/npm-Installer-CB3837?logo=npm&logoColor=white)](plugins/installer/)

</div>

EverResearch gives your AI agent the tools to understand and maintain a research project. It maps how datasets, models, and code fit together, runs project checks, and connects experiments to their configurations and results so you can reproduce past work and build on it. It works with your existing project files, Python environments, and compute.

<a id="install"></a>

## Quick Start

### Install in your AI agent

EverResearch is available as native plugins and portable Agent Skills for the following platforms. Choose the agent you already use.

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

<details>
<summary><b>Codex</b></summary>

```bash
codex plugin marketplace add OpenSAE/EverResearch
codex plugin add ever-research@ever-research
```

</details>

<details>
<summary><b>Claude Code</b></summary>

Run these commands in Claude Code:

```text
/plugin marketplace add OpenSAE/EverResearch
/plugin install ever-research@ever-research
```

</details>

<details>
<summary><b>GitHub Copilot CLI</b></summary>

```bash
copilot plugin marketplace add OpenSAE/EverResearch
copilot plugin install ever-research@ever-research
```

</details>

### Install with Agent Skills

Run the following command from your research project directory to install the complete set of skills:

```bash
npx --yes skills add https://github.com/OpenSAE/EverResearch/tree/main/plugins/agent-plugin --all -y
```

Hosts that execute the tools need Python 3.11, 3.12, or 3.13. On first use, skills installed from GitHub download and verify EverResearch's pinned Python package, then cache it. Downloadable plugin ZIPs include the runtime.

### Install from the terminal

Install the standalone CLI from [PyPI](https://pypi.org/project/ever-research/):

```bash
uv tool install ever-research
```

EverResearch 0.2.1 adds Python 3.13 support. You can also install the
[same build from GitHub](https://github.com/OpenSAE/EverResearch/releases/download/v0.2.3/ever_research-0.2.3-py3-none-any.whl):

```bash
uv tool install --python 3.13 https://github.com/OpenSAE/EverResearch/releases/download/v0.2.3/ever_research-0.2.3-py3-none-any.whl
```

From a source checkout, install with `python -m pip install .` and run
`rh doctor --json`. Use `python -m pip install -e .` for development.

Or install the CLI and project-local skills together using the [npm installer](plugins/installer/). It detects installed agent commands automatically:

```bash
npm exec --yes --package=https://github.com/OpenSAE/EverResearch/releases/download/v0.2.3/opensae-ever-research-0.2.3.tgz -- ever-research
```

### Start with your own research project

Open an existing research project in your agent and ask:

> Use EverResearch to understand my research project. Map the existing datasets, models, tasks, configurations, and experiments. Identify improvements that would make the project easier to maintain and reproduce, and propose a plan before changing files.

Or start directly from the terminal:

```bash
rh projects project check ./MyProject
```

EverResearch uses the model configured in your agent. Full project operations require an execution environment with access to the project files and its dependencies. Agents with file access alone can still inspect the available materials and propose changes.

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

Here are a few things you can ask your agent to do:

- Add a new dataset and make it available to the existing training and evaluation tasks.
- Integrate a new model without duplicating the existing experimental pipeline.
- Reproduce a previous experiment using its recorded configuration.
- Compare experimental results and trace each result back to its source configuration.
- Explain how a research repository works before making changes to it.

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
| [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3) | Depth estimation |
| [FastVLM](https://github.com/apple-aiml-research/ml-fastvlm) | Efficient vision-language modeling |
| [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) | Text embeddings and retrieval |
| [LightEval](https://github.com/huggingface/lighteval) | Language model evaluation |
| [LLMLingua](https://github.com/microsoft/LLMLingua) | Prompt compression and LLM efficiency |
| [RF-DETR](https://github.com/roboflow/rf-detr) | Object detection |
| [SAM2](https://github.com/facebookresearch/sam2) | Image and video segmentation |
| [VGGT](https://github.com/facebookresearch/vggt) | 3D visual geometry |

The CUB-200 template is included as a runnable example. Download the [BirdStudy example](https://github.com/OpenSAE/EverResearch/releases/download/v0.2.3/ever-research-0.2.3-example.zip) or explore the [research project templates](src/harness/projects/templates/).

These projects illustrate the application of a common organizational approach to different research tasks. The original projects belong to their respective authors.

## Roadmap

EverResearch is building toward a research environment in which both humans and AI agents can accumulate knowledge and make sustained scientific progress.

- **Long-Horizon Research:** Enable agents to plan, execute, and refine research over extended periods, building on previous experiments.
- **Knowledge Interface:** Help agents connect scientific concepts, evidence, code, and results to contribute to research discussions and paper writing.
- **Research RSI:** Explore how agents can improve their research capabilities through domain knowledge, experimental feedback, and human supervision.

## Documentation and Contributing

- [Agent plugins and installation](plugins/)
- [Research project organization and workflows](src/harness/projects/README.md)
- [CLI, npm installer and local usage](plugins/installer/)
- [Build from source and optional MCP integration](src/harness/utils/release/README.md)

We welcome contributions from researchers and developers. Share a research workflow, propose a reusable skill, or help bring EverResearch to another agent ecosystem through [GitHub Issues](https://github.com/OpenSAE/EverResearch/issues) and pull requests.

## License

EverResearch is released under the [Apache 2.0 License](LICENSE). Included third-party components retain their respective licenses.
