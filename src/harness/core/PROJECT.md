# 项目接入与本机资源

## 目的和主要功能

说明父工作区的一级布局，以及如何绑定项目源码、数据目录、Python 和定位保留的结构成果。

## 适用范围

用于初始化工作区、登记科研项目、配置本机资源或查询结构成果，适用于任何项目组织和运行环境。

## 工作区一级目录

```text
workspace/
├── .researchharness-workspace.json
├── ResearchHarness/
├── data/
├── SAEBase/
└── <其他科研项目>/
```

`workspace/` 是本机选定的父目录。各项目仓库、ResearchHarness 和共享 `data/` 平级。数据可按名称和版本组织在 `data/<数据集>/<版本>/`。有共享权重或环境时，可额外使用 `weights/`、`envs/`。项目内部的 `conf/`、`experiment/` 和专用数据仍由项目管理。ResearchHarness 内的 `.workspace/` 保存本机状态和结构成果。

已有 ResearchHarness 仓库时运行 `rh projects --harness-root <ResearchHarness目录> init-workspace`。它在该仓库的父目录创建 `data/`（如有需要）和工作区标识。标识记录 ResearchHarness 的一级目录名。在已初始化的工作区中，`rh projects` 从当前目录向上查找标识。也可在工作区之外通过 `--harness-root` 指定完整的 ResearchHarness 源码目录。已安装的命令使用所选源码目录的共享技能和状态。

项目登记输入的相对路径从命令执行目录起算。绑定数据和 Python 时，输入的相对路径从该项目根起算。项目与数据位于同一工作区时，登记记录使用工作区相对路径，工作区内项目的共享技能链接也使用相对路径。外部目录继续用本机绝对路径。旧绝对绑定继续读取，搬迁前可在原位置重新登记项目、绑定相关资源并应用共享技能。Python 环境本身遵循其安装和搬迁条件。

| 资料 | 用途 |
| --- | --- |
| `.workspace/harness/core/central/project_roots.json` | 项目标识到源码目录的本机映射。由 `rh projects register` 写入，已登记项目直接沿用。 |
| `src/project/<项目>/project.yaml` | 已知项目的中央身份和可选的共享技能设置。项目新登记时默认启用，应用时同步项目链接。 |
| `src/project/<项目>/README.md` | 工程入口和一线反馈，按项目实际情况保存。 |
| `.workspace/harness/projects/resources/` | 每个项目的具名数据目录和所选 Python。 |
| `.workspace/harness/projects/structure/` | 独立结构页面、来源和针对内容摘要的审阅记录。 |

项目自己的代码、科研配置、运行环境要求和实验结果归项目。中央数据和 Python 路径是本机选择，启动后由项目的原有入口处理。现有项目可以用命令参数或环境变量取得具名目录。记录来源版本时，可使用仓库提交或能重新定位相同输入的快照标识。

[项目共享技能与本机操作](../projects/README.md)说明如何实际安装共享技能、选择本机数据与 Python 并查询结构成果，适用于项目接入与日常设备切换。
