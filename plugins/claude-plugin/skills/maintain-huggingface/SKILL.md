---
name: maintain-huggingface
description: Review or maintain Hugging Face datasets and Spaces. Use to check repository or runtime status, download assets, publish selected files, or manage Space settings.
---

## Runtime compatibility

The repository skills are synchronized with EverResearch source. This distribution's launcher uses the published EverResearch 0.3.1 wheel. For source workflows that require the `.everresearch/` setup or a source-only command, use the CLI from the corresponding [EverResearch source checkout](https://github.com/OpenSAE/EverResearch/commit/9b036cb2109788a8545724a03c313502d255d187). Use the project's existing maintenance entry point when working with the published runtime.

# Hugging Face 访问与维护

## Run the EverResearch CLI

Use Python 3.11, 3.12, or 3.13 to run `scripts/rh.py` from the current skill,
followed by the arguments after `rh`. For example, pass `projects project check <project-path>` to check a
project. Use `${CLAUDE_SKILL_DIR}` in Claude Code or Cowork and the staged skill
directory in Claude web.

The launcher uses the packaged runtime when available. GitHub marketplace
installs download the pinned wheel once and verify its checksum before use.
The launcher creates a private environment and may fetch Python dependencies.
With no Python execution available, review the files you can
access and tell the user which automated checks you could not run.

For a separate terminal installation, the official PyPI package is
`ever-research` from OpenSAE. The PyPI project named `researchharness` is
maintained separately.

## 目的和主要功能

使用 Hugging Face 官方命令和 Python 客户端，访问用户账号并维护明确指定的 Spaces 与数据集。将用户的自然语言请求落实为仓库读取、文件提交、运行状态查询和指定的维护操作。

## 适用范围

用户要求查看 Hugging Face 登录身份、仓库及文件，创建或更新数据集和 Space，下载指定内容，或者管理 Space 运行与配置时使用。任务对象由本次指定的账号或组织、完整仓库名称、仓库类型、文件范围和操作决定。模型训练、推理服务部署与数据加工按用户单独提出的任务处理。

## 工具与账号

- 使用已安装的 `hf` 命令及 `huggingface_hub` Python 包。先查看本机命令帮助或方法签名，使用当前版本实际支持的接口。参考官方[命令说明](https://huggingface.co/docs/huggingface_hub/en/guides/cli)了解访问与文件操作，参考 [Space 管理说明](https://huggingface.co/docs/huggingface_hub/en/guides/manage-spaces)了解运行与配置操作。
- 使用 `hf auth whoami` 确认当前登录身份。Python 采用 `HfApi()`，复用现有登录或 `HF_TOKEN` 环境变量。账号和组织从当前身份与用户指定目标中确定，整个技能可随文件夹移动。
- 需要登录时，指导用户在自己的终端使用 `hf auth login`，或通过运行环境的凭据入口配置 `HF_TOKEN`。令牌、Space 密钥及完整认证响应保留在凭据处理环节；对话、命令参数、草稿和日志只记录身份、密钥名称及操作结果。
- 登录成功说明身份已确认；具体仓库的读写能力依据该仓库的访问结果与凭据权限判断。用户指定组织仓库时，使用该组织的完整仓库名称。

## 把请求落实为操作

1. 确定对象：完整仓库名称为 `账号或组织/仓库名`；类型为 `dataset` 或 `space`。文件操作同时确定本地来源、远端相对路径，以及用户指定的分支。
2. 查询已有状态：读取目标仓库信息、文件清单，必要时读取相关说明或 Space 配置。新建仓库时明确名称、类型、公开或私有；新建 Space 同时确定静态页面、Gradio 或 Docker 类型。
3. 用户已经明确目标和操作时，直接完成授权范围内的工作。会改变目标或效果的关键信息缺失时，先询问该项。删除远端内容、改变可见性、扩大上传范围或增加付费资源，各自依据用户的明确要求执行。
4. 上传前准备内部副本，查看将提交的实际文件与对应远端内容。根据当前请求执行新增和更新；远端删除依据明确选定的删除范围执行。
5. 报告实际提交、下载位置或运行状态，提供仓库或 Space 链接。提交返回成功与应用运行就绪分别报告；查询状态采用有限次数，仍在构建时说明当前状态。

## 本地资料与上传副本


对于已安装版本，用 `rh guide skill-state maintain-huggingface` 定位可写目录，在该目录保存下文的本地产物。启动本技能的脚本时，对该进程设置 `RH_SKILL_WORK_DIR` 为这个路径。

本技能目录由当前 `SKILL.md` 所在位置确定。每次产生资料时使用内部目录 `results/<用途与时间或其他标识>/`，按需保存 `staging/` 上传副本、`downloads/` 下载内容、缓存和操作记录。

上传从用户选定的目录或文件复制到 `staging/`，以该内部副本提交。副本初始文件内容与选定范围一致；原输入保持只读。需要新增说明、修改数据集卡片、整理目录或补充 Space 配置时，在内部副本按本次要求处理。明确本地文件与远端相对路径的对应关系，提交前只展示必要的变更摘要。

复制时识别符号链接的实际目标；链接指向选定范围外的内容时，明确实际上传对象后处理。上传使用选定的文件集合，凭据、准备日志与缓存分别留在各自用途目录。

下载目录显式指向技能内部；用户明确指定外部交付位置时按该位置交付，本地准备仍在技能内。需要 Hub 缓存时，在启动官方工具前将 `HF_HUB_CACHE` 指向本次任务内部缓存目录，认证仍沿用已有位置。

每个任务目录使用 `log_updates.jsonl` 记录新增或更新的本地产物：带时区时间、技能内相对路径、简要内容、实际来源工具或文件。远端操作记录仓库、类型、文件范围、提交标识或运行状态；密钥操作只记录名称和成功与否。

### 下载已有资产并建立本地工作目录

用户要求下载或建立仓库本地副本时，使用本技能的 `scripts/download_assets.py`。它通过官方客户端下载指定提交的全部仓库文件，以账号或组织、仓库类型及仓库名组织本地目录。下载前读取文件数量和大小，结合实际磁盘空间确定可完成本次范围。

```text
results/<任务标识>/
├── inventory.json
├── log_updates.jsonl
├── cache/
└── <账号或组织>/
    └── spaces/、datasets/ 或 models/
        └── <仓库名>/
            ├── repository.json
            ├── source/
            └── checkout/
```

`source/` 保存本次固定提交的原始文件，`checkout/` 是独立的维护工作副本，两者保持仓库内原有文件结构。`repository.json` 记录远端地址、仓库类型、提交版本和文件清单。后续编辑在 `checkout/` 进行，上传准备从选定工作内容复制到 `staging/`。更新远端来源时建立新的具名任务，保留已有版本和本地修改。

将 `<skill-directory>` 替换为本技能完整路径，按本次实际范围重复 `--repo`：

```bash
python <skill-directory>/scripts/download_assets.py --task <任务标识> \
  --repo space:<账号或组织>/<仓库名> \
  --repo dataset:<账号或组织>/<数据集名>
```

普通网络下载中断后，使用相同任务名、相同仓库清单及 `--resume` 继续固定版本的下载。程序保留已完成的工作副本；已出现本地复制文件而记录尚未完成时，先查看该任务的实际文件，再确定继续方式。本地副本保存仓库文件和来源提交，Git 历史、Space 的服务端密钥及运行磁盘资料分别按用户提出的额外范围处理。

## 常用操作

Python 操作统一从下面的官方客户端开始；示例中的名称和路径替换为当前任务实际值。示例供按任务选择调用，创建、上传、暂停和配置分别对应用户请求。

```python
from huggingface_hub import HfApi, hf_hub_download

api = HfApi()
```

### 读取账号资源和仓库

```python
# namespace 来自当前账号或用户指定的组织；按需要增加返回数量。
datasets = [item.id for item in api.list_datasets(author=namespace, limit=20)]
spaces = [item.id for item in api.list_spaces(author=namespace, limit=20)]
info = api.repo_info(repo_id=repo_id, repo_type=repo_type)
files = api.list_repo_files(repo_id=repo_id, repo_type=repo_type)
```

按需要读取选定文件，使用明确的下载位置。数据集下载保留 `repo_type="dataset"`，Space 文件使用 `repo_type="space"`。

```python
path = hf_hub_download(
    repo_id=repo_id, repo_type=repo_type,
    filename=remote_path, local_dir=download_directory,
)
```

### 创建、上传及更新数据集

```python
url = api.create_repo(repo_id=repo_id, repo_type="dataset", private=private)
commit = api.upload_folder(
    repo_id=repo_id, repo_type="dataset", folder_path=staging_directory,
    path_in_repo=remote_directory, commit_message=message,
)
```

单文件更新使用 `api.upload_file(path_or_fileobj=staged_file, path_in_repo=remote_path, repo_id=repo_id, repo_type="dataset", commit_message=message)`。更新数据集卡片时，将 `README.md` 作为实际选定的上传文件。保留用户的数据格式、划分和许可；需要新增这些信息时依据实际资料填写。

### 创建、更新和运行 Space

```python
url = api.create_repo(
    repo_id=repo_id, repo_type="space", space_sdk=sdk, private=private,
)
commit = api.upload_folder(
    repo_id=repo_id, repo_type="space", folder_path=staging_directory,
    path_in_repo=remote_directory, commit_message=message,
)
runtime = api.get_space_runtime(repo_id=repo_id)
```

Space 代码、依赖与 `README.md` 中的应用类型和入口配置保持一致。重启调用 `api.restart_space(repo_id=repo_id)`，暂停调用 `api.pause_space(repo_id=repo_id)`；从暂停恢复使用普通重启。硬件、存储和其他收费设置按明确指定的资源要求处理。

### 设置变量和密钥

普通配置调用 `api.add_space_variable(repo_id=repo_id, key=key, value=value)`。密钥从用户指定的凭据入口或环境变量读取，再调用 `api.add_space_secret(repo_id=repo_id, key=key, value=secret_value)`。完成后报告名称与操作状态，配置变更可能触发 Space 重启，随后查询实际运行状态。

## 常见结果处理

- 认证失败时，确认当前凭据来源并指导重新登录；权限不足时，核对仓库类型、完整名称和凭据授权范围。
- 仓库未找到时，结合登录身份与目标名称说明实际访问结果；私有仓库的访问能力以服务返回为准。
- 文件较多或较大时，按实际规模选用官方大目录上传能力，准备副本与缓存继续保存在本技能内。
- 网络中断或写入结果不明时，先读取远端文件或提交状态，再决定是否重试。提交冲突时重新读取当前版本，并保持用户确定的变更范围。
- 失败报告保留必要的状态码和原因；密钥值及带认证信息的地址在输出前移除。
