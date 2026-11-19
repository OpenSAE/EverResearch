# CUB-200 分类参考项目

## 目的和主要功能

训练 ResNet18 加 MLP 分类头，在 CUB-200-2011 上做 200 类整图分类。作为 ResearchHarness 的参考项目，同时展示组件组织、实际运行、性能检查、结果交付与功能变更的维护方式。

## 适用范围

从 ResearchHarness 源码目录使用，或将整个 template 目录复制到独立工作区作为新项目起点。项目使用本地 Python 和 PyTorch，从项目根目录运行。安装使用 `python -m pip install -e .`，已有依赖时也可直接运行 `python -m cub_template`。打包时将根目录的三个组件收入 `cub_template` 命名空间，避免与环境中同名的 Python 包冲突。

## 完整布局

```text
template/
├── README.md、AGENTS.md、pyproject.toml
├── datasets/
│   ├── plugins.py
│   └── cub200/
│       ├── __init__.py                   正式入口和支持的任务
│       ├── dataset.py                    标注、图像和官方划分
│       └── offline_samples.py            CUB 分类的离线检查输入
├── models/
│   ├── plugins.py、build.py               从系列登记、共用构建
│   ├── resnet/resnet18/
│   │   ├── specs.py                      两个 ResNet18 + MLP 变体
│   │   └── model.py                      两个变体共用的实现
│   └── cnn/small_cnn/
│       ├── specs.py
│       └── model.py
├── tasks/
│   ├── plugins.py
│   ├── classification/
│   │   ├── task.py                        任务接口、供预检使用的实际步骤
│   │   └── operation.py                   训练、评估和指标
│   └── precheck/
│       ├── task.py                        独立预检与性能入口
│       ├── gate.py                        正式任务调用预检
│       ├── timing.py                      阶段计时
│       └── performance.py                 基线瓶颈和候选比较
├── cub_template/
│   ├── cli.py、__main__.py                 命令入口
│   ├── registry.py、contracts.py           登记查询、数据与任务结果接口
│   └── runtime/
│       ├── config.py、environment.py       配置组合、运行环境
│       ├── runner.py                      选组件、验证、预检及分发
│       └── records.py                     运行身份、状态及结果清单
├── conf/
│   └── config.yaml                       唯一的默认配置
├── experiment/                           固定的实验根
│   └── <数据集>/<模型>/<任务>/<subname>/<运行标识>/
│       ├── config.yaml                    单次运行的生效配置
│       ├── metadata/manifest.json         状态和产物索引
│       ├── reports/
│       └── artifacts/
├── tests/
│   ├── test_workflow.py                   正常入口和结果回归
│   └── test_boundaries.py                 配置隔离、数据划分与候选失败
└── doc/code/development/
    ├── layout.md
    └── engineering.md
```

`datasets/`、`models/`、`tasks/` 是必备目录，各自维护组件登记。和 SAEBase 一样，正常入口组合配置，运行层根据配置选任务，任务定义计算并返回结构化结果。预检可以独立选择，也在正式训练前由运行层调用。运行清单记录预检回执、任务结果和产物路径。

数据根由配方或 `--data-root` 指定。运行根固定为项目一级目录 `experiment/`，由程序从项目根定位。正常运行按 `<数据集>/<模型>/<任务>/<subname>/<运行标识>/` 保存。用 `--subname` 给实验取一至三个描述用途的词，例如 `scratch_baseline` 或 `imagenet_finetune`。重复运行同一实验时沿用名称，由程序创建独立的运行目录。配置或组件选择失败的清单归 `unresolved/<subname>/`。正式结果通过 `metadata/manifest.json` 定位。

[模板布局示例](doc/code/development/layout.md)说明各目录负责什么、何时扩展，供复制模板、增加组件和调整项目布局时使用。

## 项目维护的技能入口

共享维护技能位于 ResearchHarness 主仓库的 `.agents/skills/`。本模板提供组件登记、独立预检、性能比较和结果检查的可运行示例。作为独立项目使用时，登记项目并通过 `rh projects apply <项目标识>` 生成项目侧的技能链接。

## 离线演练

在项目目录执行。运行从 `conf/config.yaml` 读取默认值，`--set` 选择组件或覆盖参数。

```bash
offline=(
  --subname offline_check
  --set dataset=synthetic --set model=resnet18_mlp_small
  --set runtime.device=cpu --set runtime.workers=0
  --set training.batch_size=2 --set training.epochs=1
  --set benchmark.samples=4
)
python -m cub_template precheck "${offline[@]}"
python -m cub_template run "${offline[@]}"
python -m cub_template benchmark "${offline[@]}" --candidate-workers 1
```

用 `--config <运行目录>/config.yaml` 读取先前保存的配置。运行仍需给出 `--subname`，并生成新的运行目录。复跑历史实验时，配置结合清单中的源码版本使用。已归档的 ImageNet 微调对应其试跑副本。

性能预检报告比较当前工作进程数和候选值，显示基线耗时最长的阶段、结果一致性及推荐值。需要正式验证时，用同一配方的 `--set runtime.workers=<推荐值>` 运行，再核对实际工作量与总耗时。每条命令打印运行目录。用 `python -m cub_template inspect <运行目录>` 读取运行状态和产物路径。离线配方的输入标为 `synthetic`，用于验证工作过程。

## 正式 CUB-200 基线

准备 [Caltech-UCSD Birds-200-2011 官方数据](https://www.vision.caltech.edu/datasets/cub_200_2011/)，将 `--data-root` 指向包含 `images/`、`images.txt`、`image_class_labels.txt`、`train_test_split.txt` 的解压目录。运行配置只读取本地数据，模型从随机权重开始。官方划分用于固定 5,994 张训练图和 5,794 张测试图。

```bash
python -m cub_template precheck --subname scratch_baseline --data-root "$cub_data"
python -m cub_template run --subname scratch_baseline --data-root "$cub_data"
```

先将 `cub_data` 设置为本机数据目录。训练用随机裁剪和翻转，正式测试用确定性缩放和中心裁剪。按配置训练固定轮数，最终权重在官方测试集评估一次，报告平均交叉熵和 Top-1。预检和性能比较使用训练集的小样本，保留官方测试集用于最终评估。

## 结果与后续工作

- `config.yaml` 保存实际生效的配置。
- `metadata/manifest.json` 保存配置引用、数据来源、软件源文件哈希、实测环境、状态和相对产物路径。
- `reports/` 保存阶段指标、预检、性能比较或最终测试。训练每轮保存已有指标。
- `artifacts/model.pt` 保存本次训练的最终模型权重。
- 数据缺失时，清单以 `blocked` 记录具体缺项和恢复方式。运行报错记录阶段和原因。

项目维护方法见 [工程工作示例](doc/code/development/engineering.md)。项目助手先依据真实文件和运行结果处理常规工程问题，可以把共性发现反馈给中央。
