# 项目共享技能与本机操作

## 目的和主要功能

列出项目整理与维护的技能入口，向科研项目同步共享技能，维护本机数据和 Python 选择，保存可复查的结构成果。

## 适用范围

用于选择项目整理或维护技能，以及对选定项目执行接入、技能开关、本机资源绑定或结构成果审阅。陌生项目可先从实际入口摸底，按需要登记。

## 陌生项目整理与日常维护

**[`build-project`](../../../.agents/skills/build-project/SKILL.md) 是陌生科研项目挂载、梳理和结构整理的主要入口。** 从实际运行入口和已有产物识别职责，整理项目布局、基础层和组件说明，再将实际入口和待整理事项交给后续维护。

维护已有项目时，按具体工作选择专项技能。整理陌生项目时，也可调用同一组技能处理对应环节。

| 技能 | 适用工作与职责 |
| --- | --- |
| [`maintain-base`](../../../.agents/skills/maintain-base/SKILL.md) | 接通命令、配置、数据、模型与任务，维护分发、共用运行资源和结果读写。 |
| [`maintain-dataset`](../../../.agents/skills/maintain-dataset/SKILL.md) | 增改移除数据集与预设，维护样本准备、划分、登记和任务读取。 |
| [`maintain-model`](../../../.agents/skills/maintain-model/SKILL.md) | 增改移除模型或变体，维护构造、权重加载及任务兼容。 |
| [`maintain-task`](../../../.agents/skills/maintain-task/SKILL.md) | 增改移除科研任务、模式或结果接口，维护计算、指标和结果交接。 |
| [`maintain-experiment`](../../../.agents/skills/maintain-experiment/SKILL.md) | 调整默认实验配置或单次参数，执行、跟踪、恢复、读取或排查实验。 |
| [`maintain-optional`](../../../.agents/skills/maintain-optional/SKILL.md) | 维护独立脚本、测试、组件文档和随项目保存的外部文件。 |

## 项目接入

[项目接入与本机资源](../core/PROJECT.md)规定 ResearchHarness、共享数据和各科研仓库的一级位置，以及项目和资源路径的解析方式。初始化工作区或搬迁项目时查阅。以下命令从父工作区执行，示例项目仓库位于 `example/`。

```bash
rh projects --harness-root ./ResearchHarness init-workspace
rh projects register example --path ./example
rh projects status example
rh projects apply example
rh projects set example --skills off
```

`manage.py` 读取中央 `.agents/skills/` 下有 `SKILL.md` 的技能目录，同步项目中的中央链接及接入说明。若项目已用 `.agents/skills/` 作为自己的目录别名，中央技能放在 `.agents/researchharness-skills/`。同名自有技能保留，接入时报告冲突。现有项目的中央身份、共享设置和工程经验位于 `src/project/<项目>/`。项目自己的代码审阅、计划与协作授权使用项目的 GitHub 流程。

## 项目工程说明

- [科研项目目录与文件职责](LAYOUT.md)说明布局、文件归属和调用关系，适用于接入、整理和扩展采用该布局的项目。
- [项目工程协议](PROTOCOL.md)说明项目检查、预检、性能、环境、结果与人工判断，适用于采用共同工程约定的项目。
- [CUB-200 分类参考项目](template/README.md)演示组件、预检和结果的配合，适用于对照可运行的工程样例。

## 本机数据、Python 和结构成果

`rh projects bind`、`resources` 和 `run` 管理本机路径并用所选 Python 调用项目原有入口。使用 `{data:名称}` 把已登记的数据目录交给项目的参数或环境变量。

`rh projects structure add` 接收由 ExtractStructure 导出的可信独立 HTML，以及来源版本和分析范围。使用 `list` 或 `show` 查找页面，使用 `review` 记录对该版本的决定。查看页面直接打开命令返回的本机路径。

[使用示例](../../../README.md)介绍安装和各命令的具体调用，适用于新项目接入和既有项目的本机操作。
