# 工程工作示例

## 目的和主要功能

用真实目录、程序和产物说明项目怎样增加功能、检查改动、比较性能和提交人类审阅。

## 适用范围

供维护本项目及参照此结构组织其他项目的助手阅读。协议中的共同要求见上级 projects/PROTOCOL.md，具体命令见项目 README.md。

## 从工作需要定位文件

| 工作 | 负责位置 | 改完后从哪里看效果 |
| --- | --- | --- |
| 支持另一种输入 | datasets 下新增负责模块，在配置与入口选择该输入 | 用预检查样本形状、标签和来源字段 |
| 增加模型或分类头 | models 下新增实现，在正常入口选择该模型 | 用现有预检确认模型可完成前反向，再运行相关模型检查 |
| 修改跨组件指标 | tasks/classification/operation.py 与报告读取者 | 比较同一批样本的原新损失、准确率和结果格式 |
| 修改运行资源设置 | runtime/config.py 与所选运行配方 | 查询运行清单中的实际设备、依赖和线程设置 |
| 调整结果格式 | runtime/records.py 与读取清单的入口 | 对照已保存的清单及 inspect 输出，确认已有调用者的读取条件 |

## 维护技能对应的实际操作

| 操作 | 在模板中从哪里查起 | 怎样判断处理完成 |
| --- | --- | --- |
| 增加一种数据来源 | `datasets/cub200/dataset.py`、同目录的离线样本以及 `conf/config.yaml` | 选定新来源后，正式预检能够使用代表性样本，并记录实际来源 |
| 修改一个模型变体 | `models/resnet/resnet18/specs.py`、`conf/config.yaml` 和实际使用该预设的配方 | 从生效配置和预检输出核对修改，按需检查同系列保留变体 |
| 修改分类任务的指标 | `tasks/classification/task.py` 与 `operation.py`，再追到结果写入和 `inspect` | 报告和清单能定位同一次运行的指标，并记录含义及历史可比性 |
| 移除一个选项或组件 | 从对应登记查到默认配置、别名、配方和直接调用 | 更新保留调用后移除选定范围。移除整个组件时再处理专属实现、说明和检查 |
| 诊断一次实验 | 从 `inspect` 读取运行清单，沿失败阶段定位输入、任务或公共运行层 | 从独立预检或小规模运行取得处理依据，再由清单定位实际产物 |

## 从 SAEBase 采用的扩展路径

| SAEBase 的正式入口 | 模板对应实现 | 扩展时的实际做法 |
| --- | --- | --- |
| conf/config.yaml 的 Hydra defaults | conf/config.yaml 在同一文件选择并定义 dataset、model、task 组 | 增加模型配置后，用默认配置与覆盖项切换 model=resnet18_mlp_small |
| models/plugins.py、tasks/plugins.py 与 saebase/registry.py | 三类组件自己的 plugins.py 和 cub_template/registry.py | 同系列变体补系列声明和配置预设，登记读取已有系列 |
| tasks/capture/task.py 与 operation.py | tasks/classification/task.py 与 operation.py | task.py 承接验证和运行接口，operation.py 实现任务计算 |
| tasks/precheck/task.py、gate.py 与 saebase/runner.py | tasks/precheck/task.py、gate.py 与 cub_template/runtime/runner.py | 可以单独选择预检，训练在同一路径留下自动预检回执 |
| saebase/results.py 和 runtime/experiment_results.py | cub_template/contracts.py 与 runtime/records.py | 任务返回 EvaluationResult，运行层保存结果和清单 |

同系列新增变体只补 models/resnet/resnet18/specs.py 和 conf/config.yaml。从默认配置选择 resnet18_mlp_small，运行预检和训练，读取清单中的选择及报告。两个变体共用 model.py、同一登记和分类任务。新增正式数据集时使用自己的目录，再更新数据集登记和配置预设。

本模板的预检在同一进程用有界训练样本检查正式步骤，隔离随机状态后再开始训练。接入 CUDA、数据准备或独立进程检查时，以该项目的实际资源和预算决定实现。命令与配置见项目 README。

## 已实现的改动样例：用实测决定工作进程数

分类任务提供固定的训练样本视图和实际前向。`tasks/precheck/timing.py` 在计时边界同步 CUDA，`tasks/precheck/performance.py` 比较配方当前的工作进程数与候选值。默认实际配方用 32 张图，预热一次，重复三次。

每次分开记录加载器启动、等待数据、前向与数据传输、关闭、总耗时与 GPU 显存峰值，模型初始化在准备耗时中单列。预检按基线阶段中位数定位瓶颈，并报告样本、重复次数、候选耗时和一致性。输出 logits 在给定误差内、预测类一致、已有 CUDA 显存预算满足且候选更快时才推荐候选，否则沿用当前配置。通过 `--set runtime.workers=<值>` 选择推荐值可验证正式任务开销。局部前向的比较范围随报告保存。

默认预检使用正式配置的工作进程数，对训练视图执行一个最多两图的参数更新，并在确定性训练视图上执行一次评估。正式配方会出现单图尾批时，预检额外实跑这一批，错误在正式训练开始前写入清单。正式训练重新初始化。需要限定整条预检命令的墙钟时间时，可用外部 `timeout --signal=INT --kill-after=10s 120s`，时间包含索引和模型准备。中断记录为 `partial`，强制终止后留下的 `running` 清单表示仍需核对这个运行。

候选在实际运行中失败时，性能报告保存已完成的基线、失败原因及保留当前配置的决定。运行清单记录包含系列默认值的实际模型设置，便于随后对照配方和结果。

## 人类审阅样例：采用新的初始化方案

当前基线使用随机初始化。若提出引入外部预训练权重，记录来源、训练数据范围、额外下载与训练成本，并说明它与原基线的可比性。Caltech 官方指出 CUB 图像与 ImageNet 存在重叠，这会影响采用 ImageNet 权重的结果解释。用同一数据划分、相同指标和明确的运行身份呈现代表结果，让人类决定采用范围。工程上等效的文件归位、失败信息修复与批量读取优化按现有授权推进。

## 项目与中央共同更新

保留协议版本、实际实现位置和代表性运行证据。新项目可以复制完整目录，先以合成输入演练自己的正常入口，再替换负责的数据集、模型和任务部分。协议有歧义或多个项目出现相同问题时，记录真实案例、拟改条款或实现与受影响的调用者，回到中央维护。项目运行的清单遵循协议字段，现有 inspect 提供可读结果。

更新中央协议时，同一次维护改好模板中对应的实现、目录、配置或适用说明。目录规则的对照入口是本项目 README.md。项目默认配置见 conf/config.yaml，生效配置见 experiment 下的对应运行，正常入口回归和组件边界检查直接放在 tests。出现独立的集成测试或稳定的回归测试组时，再按协议分别归入 integration 或 product。移动文件后同步入口、配置引用及测试发现位置。
