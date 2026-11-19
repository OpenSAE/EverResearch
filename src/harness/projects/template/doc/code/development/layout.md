# CUB 分类模板的布局示例

## 目的和主要功能

把中央的目录规则对应到可运行的分类实现，说明模板采用了哪些目录，以及有新增用途时怎样扩展。

## 适用范围

用于参照模板建立项目、增加组件或调整布局。中央工作区使用 [科研项目目录与文件职责](../../../../LAYOUT.md) 确定一级布局、二级目录的启用条件、职责和取名规范。复制到独立项目后，使用所绑定中央的同一份规范。

## 实际位置和启用条件

| 规则 | 本项目的例子 | 何时扩展 |
| --- | --- | --- |
| 根目录提供入口 | README.md 给出正常命令和结果入口，AGENTS.md 提供工作规则，pyproject.toml 定义安装和命令 | 有新的稳定入口时同步更新项目说明 |
| 基础层负责连接组件 | cub_template/cli.py 分发动作。各类 plugins.py 登记组件，registry.py 统一查询，runtime/runner.py 组织实际检查与执行。runtime/environment.py 采集环境，runtime/records.py 保存清单。模板的运行包承担新项目中常用的 base/ 职责 | 有稳定外部调用时可设 api/。配置合成形成独立用途时可扩展 runtime/cfg/ |
| 组件留在自己的作用范围内 | 根目录的 datasets/cub200/dataset.py 提供官方样本和划分，datasets/cub200/offline_samples.py 提供独立的合成配方输入。models/resnet/resnet18/specs.py 声明两个共用实现的变体，tasks/classification/task.py 接入任务接口，operation.py 负责训练和指标。tasks/precheck 是独立任务 | 正式新数据集建立自己的目录，同系列模型补 specs.py 和配置目录中的预设。新架构才增加系列实现 |
| 组合配方跟任务走 | conf/config.yaml 将官方数据、模型和分类任务组合，离线演练从同一默认配置选择合成数据 | 默认配置集中一处，实验用 subname 命名，生效配置保存到对应运行目录 |
| 检查按持续用途保存 | tests/test_workflow.py 用少量离线回归覆盖运行清单和缺数据分支 | 形成独立回归组或集成链路时再建 tests/product 或 tests/integration，共用固定输入可归 tests/fixtures |
| 从 README 找到组件说明 | 模板 README 给出正常命令，doc/code/development 保存目录与改动示例 | 建立独立项目时强烈推荐添加 doc/datasets.md、doc/models.md 和 doc/tasks.md，记录共有参数和各条目。按实际用途增加科研知识、环境说明和独立操作入口 |
| 数据和结果可独立定位 | 配方声明数据路径，入口接受实际数据根。结果写入项目一级目录 experiment，按数据集、模型、任务、实验名称和运行标识组织，metadata/manifest.json 引用报告与模型权重 | 日志和临时文件出现时才建立 logs、tmp。公开结果读取以清单为入口 |
| 接入资料按项目使用方式建立 | 本目录直接运行分类软件 | 复制并接入中央时，用实际接入入口建立 .researchharness 配置与项目技能位置 |

沿正式入口看新增功能时，先从配方找到数据、模型和任务，再沿正常命令确认处理和结果保存。比如加入一个可选的新模型时，保留同一任务和指标，在模型目录增加实现与配置选择，随后从预检和运行清单确认接入。需要更改指标或历史可比性时，沿 [工程工作示例](engineering.md) 组织检查和人类审阅。该说明提供功能变更、性能比较及审阅实例，供模板维护时对照。

性能预检的计时、瓶颈和候选报告在 tasks/precheck 内维护。分类任务提供实际前向和固定样本视图，运行层保存预检的回执和正式结果。

模板默认从项目根加载 conf/config.yaml，并从项目根定位 experiment/。配方声明的相对数据根从配方所在目录起算，命令行的显式数据路径从命令执行目录起算。采用共享工作区时，可把共享 data/ 中的实际资源路径传给同一个入口。
