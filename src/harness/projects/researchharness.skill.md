---
name: researchharness
description: 使用当前项目的共享维护技能、本机数据和 Python 绑定，以及已保存的结构成果。
---

# 项目与 ResearchHarness 共同维护

## 目的和主要功能

从当前项目找到共享技能、本机资源和可复查的结构成果，并将真实项目经验反馈给相应的维护说明。

## 适用范围

用于已选择项目的本机接入、技能同步、资源查询和成果读取。实际科研工作沿项目现有运行入口。

- 从项目的中央接入段落确定中央目录和项目标识。中央相对路径以项目根为起点。已初始化的工作区内可直接用 `rh projects status <项目标识>`，也可用 `rh projects --harness-root <中央目录> status <项目标识>`。用户要求同步时使用 `apply`，更改开关时使用 `set --skills on` 或 `set --skills off`。
- 用 `rh projects resources <项目标识>` 查数据目录和 Python。项目已有运行入口时，把实际路径交给它。需要由中央选择 Python 时，用 `rh projects run <项目标识> -- <项目参数>`。
- 用 `rh projects structure list <项目标识>` 查已保存的结构说明，按源码版本和分析范围选取。项目代码审阅、正式计划和协作授权沿项目的 GitHub 流程。
- 项目经验记录实际入口、观察到的问题、处理结果和可推广做法。值得长期保存的人类思想按 HumanInterface 的入库流程处理。

## 选择整理和维护技能

- **挂载、梳理或按模板整理陌生项目，先使用 `build-project`。** 从项目实际命令追踪代码、配置和产物的职责，整理布局、基础层和组件说明，交接给后续维护。
- **维护已有项目，按工作选择专项技能。** 数据集、模型和任务分别使用 `maintain-dataset`、`maintain-model` 和 `maintain-task`。命令分发、跨组件接入和共用运行能力使用 `maintain-base`。实验配置、参数、运行、结果读取、跟踪和恢复使用 `maintain-experiment`。独立脚本、测试、组件文档和外部文件使用 `maintain-optional`。
- 从当前项目的实际技能目录读取对应的 `SKILL.md`。绑定中央的 `src/harness/projects/README.md` 列出技能入口，并说明项目接入、共享技能同步和本机操作。
