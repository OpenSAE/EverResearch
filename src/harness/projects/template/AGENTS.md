# 分类参考项目工作说明

## 目的和主要功能

帮助助手按实际入口维护 CUB-200 分类项目，使代码、检查和结果共同示范 ResearchHarness 项目协议。

## 适用范围

适用于本模板的开发和使用，从 README.md 查找入口，按 doc/code/development/engineering.md 选择检查与审阅方式。在 ResearchHarness 源码内维护时，采用上级 projects/PROTOCOL.md 规定的工程协议。

## 工作方式

数据读取、模型、分类任务和运行支持分别归对应模块。新增功能同步处理配置、正常入口、受影响的测试和结果读取。沿用固定官方划分、指标和项目预算，在改动相关范围内主动完成检查与修复。

影响数据划分、指标、数值语义、公共入口或算力投入的方案，以实际样例和前后结果说明取舍。维护经验写入 doc/code/development/engineering.md 或具体负责模块，其他项目也需要时，提出中央协议或共享能力的相应改进。

## 共享技能

在 ResearchHarness 工作区内，沿中央 `.agents/skills/` 查阅对应技能。独立接入后的模板项目从接入时生成的项目侧技能目录读取。`maintain-dataset`、`maintain-model` 和 `maintain-task` 用于增加、修改和移除组件，`maintain-experiment` 用于执行、跟踪、恢复和调试实验。`maintain-optional` 用于独立维护脚本、测试、文档和纳入项目的外部文件。`maintain-base` 用于维护组件之间的基础协调。

数据集、模型和任务的选择从各自的 `plugins.py` 与 `conf/config.yaml` 查找。为每次实验提供一至三个词的 `subname`，描述实验用途或探索对象，生效配置随单次运行保存。训练、预检和性能比较都写入项目根的 `experiment/`。实验按 README 中的离线配方使用 `python -m cub_template run`，用 `benchmark` 做性能比较，用 `inspect` 读取既有运行清单和产物。当前训练导出最终模型权重。后续补跑从运行记录确定缺少哪一步，继续训练前查证该任务是否支持恢复完整状态。

把模板复制到独立工作区后，按普通项目登记并用 `rh projects apply <项目标识>` 生成项目侧技能链接。
