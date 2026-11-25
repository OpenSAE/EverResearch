[English](README.md) | [中文](README.zh-CN.md)

# ResearchHarness

## 目的和主要功能

ResearchHarness 为科研项目提供一组可移植的代理技能和项目检查命令
`rh`。它帮助你维护数据集、模型、任务和配置，记录可追溯的实验，
并通过项目正式入口验证改动。

## 适用范围

用于有文件和命令权限的代理环境或终端。模型由宿主环境选择。
只支持工具连接的宿主可使用可选的本地 MCP。纯聊天环境里，
你可以将项目材料交给模型出方案，再在终端运行检查。

## 开始使用

[插件目录](plugins/)包含各宿主插件和安装工具。

从插件市场目录的 `installer/` 获取 Python wheel 和 BirdStudy 示例。解压示例后，
用 Python 3.11 或 3.12 安装工具，然后在代理中打开示例项目。

```sh
uv tool install ./researchharness-*.whl
rh doctor --json
rh projects project check ./BirdStudy
rh skills install --project ./BirdStudy --agent codex
```

将 `codex` 换成你使用的宿主。随包的 `verify.py` 可以从临时环境复验安装、
项目接入和技能卸载。从自然语言提出需求后，可先请代理给出涉及的实际路径、
改动内容和验证方式，再决定是否实施。

[安装与复验指南](src/harness/utils/release/README.md)说明了 Python 与 npm 安装、
宿主插件、命令行和本地 MCP 的用法。[许可证](LICENSE)。
