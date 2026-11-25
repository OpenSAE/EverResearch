[English](README.md) | [中文](README.zh-CN.md)

# EverResearch

## 目的和主要功能

EverResearch 帮助科研人员和代理维护数据集、模型、任务、配置与实验。用同一套技能检查项目结构、整理实验记录，并通过项目原有命令验证改动。

## 适用范围

可用于有文件和命令权限的代理或终端。只有文件访问权限时，代理可以检查所提供的文件并提出方案。完整自动检查在能访问项目目录的 Python 环境运行。

## 安装

按你使用的平台打开安装说明。插件首次使用时自动准备 `rh`。从 GitHub 安装时，插件会下载并校验固定版本的 Python 包，随后复用缓存。下载的插件 ZIP 自带该包。宿主需要提供 Python 3.11、3.12 或 3.13。首次运行可能需要访问 Python 包索引来安装依赖。

| 平台 | 安装和验证 |
| --- | --- |
| Codex | [Codex](https://github.com/OpenSAE/EverResearch/tree/main/plugins/codex-plugin) |
| Claude | [Claude Code、Cowork 和网页版](https://github.com/OpenSAE/EverResearch/tree/main/plugins/claude-plugin) |
| Cursor | [Cursor](https://github.com/OpenSAE/EverResearch/tree/main/plugins/cursor-plugin) |
| Copilot CLI、Qwen Code、Skills CLI | [通用代理插件](https://github.com/OpenSAE/EverResearch/tree/main/plugins/agent-plugin) |
| Gemini CLI | [Gemini 扩展](https://github.com/OpenSAE/EverResearch/tree/main/plugins/gemini-extension) |
| OpenCode | [OpenCode](https://github.com/OpenSAE/EverResearch/tree/main/plugins/opencode) |
| OpenClaw | [OpenClaw](https://github.com/OpenSAE/EverResearch/tree/main/plugins/openclaw) |
| DeepSeek Harness | [DeepSeek Harness](https://github.com/OpenSAE/EverResearch/tree/main/plugins/deepseek) |
| 终端及其他代理 | [Python 和 npm 安装入口](https://github.com/OpenSAE/EverResearch/tree/main/plugins/installer) |

从 [PyPI](https://pypi.org/project/ever-research/) 安装 CLI，然后用自己的项目路径替换下面的 `./MyProject`。

```sh
uv tool install ever-research
rh doctor --json
rh projects project check ./MyProject
```

EverResearch 从 0.2.1 起支持 Python 3.13。也可以直接安装
[GitHub 上的同一版本](https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/ever_research-0.2.3-py3-none-any.whl)。

```sh
uv tool install --python 3.13 https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/ever_research-0.2.3-py3-none-any.whl
```

在源码目录运行 `python -m pip install .` 也会安装技能和项目指南。
开发时可用 `python -m pip install -e .`。

如果你想同时安装 CLI 和技能，在项目目录运行以下命令。

```sh
npm exec --yes --package=https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/opensae-ever-research-0.2.3.tgz -- ever-research
```

安装后，在代理里打开项目，问它“检查这个科研项目的目录结构，告诉我有哪些问题，以及你实际验证了什么”。

[构建和验收指南](src/harness/utils/release/README.md) · [许可证](LICENSE)
