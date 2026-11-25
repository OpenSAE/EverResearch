[English](README.md) · 中文

# EverResearch

EverResearch 让你现有的 AI 代理能维护科研项目。它帮助你弄清数据、模型、配置和代码怎样配合，把每次实验的配置与结果连在一起，并用项目自己的命令复现已有结果。你的代码、数据和计算环境可以继续照常使用。

<a id="install"></a>

## 快速开始

| 平台 | 安装指南 |
| --- | --- |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/codex-color.svg" alt="" width="18" height="18"> Codex | [Codex 插件](plugins/codex-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/claude-color.svg" alt="" width="18" height="18"> Claude Code、Cowork 和网页版 | [Claude 插件](plugins/claude-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/cursor.svg" alt="" width="18" height="18"> Cursor | [Cursor 插件](plugins/cursor-plugin/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/githubcopilot.svg" alt="" width="18" height="18"> GitHub Copilot CLI | [安装指南](plugins/agent-plugin/#install-in-github-copilot-cli) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/gemini-color.svg" alt="" width="18" height="18"> Gemini CLI | [Gemini 扩展](plugins/gemini-extension/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/qwen-color.svg" alt="" width="18" height="18"> Qwen Code | [安装指南](plugins/agent-plugin/#install-in-qwen-code) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/deepseek-color.svg" alt="" width="18" height="18"> DeepSeek Harness | [DeepSeek 插件](plugins/deepseek/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/opencode.svg" alt="" width="18" height="18"> OpenCode | [OpenCode 插件](plugins/opencode/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/openclaw-color.svg" alt="" width="18" height="18"> OpenClaw | [OpenClaw 插件](plugins/openclaw/) |
| <img src="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/vercel.svg" alt="" width="18" height="18"> Skills CLI | [安装指南](plugins/agent-plugin/#install-with-the-skills-cli) · [Skills.sh](https://skills.sh/opensae/everresearch) |

**终端。** 使用 Python 3.11–3.13 从 PyPI 安装。

```sh
uv tool install ever-research
rh doctor
```

离线安装包可从 [GitHub Releases](https://github.com/OpenSAE/EverResearch/releases/latest) 下载。

## 三个常用场景

| 目标 | 怎么问代理 | 你会得到什么 |
| --- | --- | --- |
| 接入项目 | “给这个项目做个整理方案，等我确认再改。” | 路径调整方案和验证步骤。 |
| 添加数据集或模型 | “把这个数据集或模型接到现有训练流程。” | 可复用的组件和对应配置。 |
| 复现实验 | “用保存的配置重跑基线，并比较结果。” | 一份新实验记录和指标对比。 |

运行 `rh projects project check ./MyProject --onboarding` 可查看只读接入预览。脚本和持续集成可用 `--strict` 判断是否通过，或用 `--json` 获取机器可读结果。

整理已有项目时，在分支上操作，合并前用原有命令验证。

## 科研工作怎么用

- **运行之前**检查本次配置，并执行项目原有的预检。
- **运行之后**跟实验结果一起保存实际生效的配置，再用 `rh projects experiment check ./MyProject` 检查记录。
- **每周回顾**请代理找出最近的实验，说明你关注的指标在哪份配置下最好。
- **投稿之前**用保存的配置复现关键结果，逐项核对输出。

[完整技能库](.agents/skills/)覆盖项目、代码、数据集、模型、任务、配置、实验和知识维护，也支持 GitHub 发布和 Hugging Face 数据集与 Space 操作。

## 已整理的项目

| 项目 | 研究方向 |
| --- | --- |
| [CUB-200](src/harness/projects/templates/cub/) | 细粒度图像分类 |
| [Depth Anything 3](src/harness/projects/templates/depth_anything_3/) | 深度估计 |
| [FastVLM](src/harness/projects/templates/fastvlm/) | 高效视觉语言推理 |
| [FlagEmbedding](src/harness/projects/templates/flag_embedding/) | 文本向量与检索 |
| [LightEval](src/harness/projects/templates/light_eval/) | 语言模型评估 |
| [LLMLingua](src/harness/projects/templates/llmlingua/) | 提示词压缩 |
| [RF-DETR](src/harness/projects/templates/rf_detr/) | 目标检测 |
| [SAM2](src/harness/projects/templates/sam2/) | 图像和视频分割 |
| [VGGT](src/harness/projects/templates/vggt/) | 三维视觉几何 |

完整训练示例 BirdStudy 可从 [GitHub Releases](https://github.com/OpenSAE/EverResearch/releases/latest) 下载。[英文 README 的 SAM2 对比](README.md#research-projects)展示了上游和整理后的目录用途。

## 接下来

我们会改进实验设置和结果的并排对比，收集更多真实仓库来改善接入报告，并持续验证各代理的安装路径。欢迎在 [GitHub Issues](https://github.com/OpenSAE/EverResearch/issues)分享实验室里最想解决的问题。

[项目维护指南](src/harness/projects/README.md) · [贡献说明](CONTRIBUTING.md) · [更新记录](CHANGELOG.md) · [引用信息](CITATION.cff) · [许可证](LICENSE)
