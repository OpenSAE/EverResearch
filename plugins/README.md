# ResearchHarness 插件

## 目的和主要功能

从仓库根目录找到各宿主的插件、共用的 `rh` 安装器和可运行的示例。插件随同一套维护技能构建。

## 适用范围

此目录供能访问本仓库的成员安装和验证插件。插件的加载方式取决于所用宿主。

| 宿主 | 文件目录 |
| --- | --- |
| Codex | [codex-plugin/](codex-plugin/) |
| Cursor | [cursor-plugin/](cursor-plugin/) |
| GitHub Copilot CLI 和 Qwen Code | [agent-plugin/](agent-plugin/) |
| Claude Code | [claude-plugin/](claude-plugin/) |
| Gemini CLI | [gemini-extension/](gemini-extension/) |
| OpenCode | [opencode/](opencode/) |
| OpenClaw | [openclaw/](openclaw/) |
| DeepSeek Harness | [deepseek/](deepseek/) |

[installer/](installer/) 提供 Python wheel、npm 安装器、DeepSeek Harness 组合包、BirdStudy 示例和校验文件。各宿主的安装命令见[安装说明](../src/harness/utils/release/README.md)。本目录也包含 Codex、Claude Code、Cursor 和 GitHub Copilot 的市场清单。
