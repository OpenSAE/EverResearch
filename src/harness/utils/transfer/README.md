# 数据传输、校验与压缩包解压

## 目的和主要功能

本文件说明如何调用 ResearchHarness 已有的 B2/rclone 数据下载、上传和校验工具，以及 tar 压缩包内容查看和选择性解压工具。它提供可读的参数解释、命令示例和实际文件处理行为说明。

## 适用范围

当用户明确要求使用 ResearchHarness 传输、校验、查看或解压文件，或者任务涉及 `utils/transfer/` 中传输与解压程序的修改时阅读。

## 两个工具

| 入口 | 实际用途 |
| --- | --- |
| `python -m harness.utils.transfer.b2` | 通过 rclone 中已配置的远程连接下载、上传或核对文件 |
| `python -m harness.utils.transfer.archive` | 查看本地 tar 内容并按路径筛选提取文件 |

以上命令默认只预览；添加 `--execute` 才尝试实际操作。两个模块均可直接处理指定文件。命令示例用于解释参数，实际传输或解压按用户明确授权执行。

B2 普通上传和下载使用 rclone 自带的传输检查，以实际传输结果记录完成状态。
额外的 `verify` 校验和独立 SHA256 文件摘要清单，仅在人类明确要求或审核批准后进行。
助手依据当前人类指令安排这些额外核验，常规传输无需附带核验步骤；收据如实记录是否执行。

## 维护传输与解压功能

制定功能改动时，先选定使用者如何取得并使用文件，以及失败后如何继续，再安排命令、结果和收据。记录关联明确的来源、目标与选定范围；失败或受阻时保留实际错误、目标处理情况和适用的下一步建议。采用本地文件场景，通过正式入口处理后读取文件与收据，确认结果能用于原定操作、重试或冲突处理。

## 前置条件和可选项目记录

- Python 3.11 / 3.12，已安装 ResearchHarness。
- 上传、下载与额外核验需安装 `rclone`，并在调用者私有配置中预先建立使用 B2 原生接口的远程连接。
- `.tar.zst` / `.tar.zstd` 解压需 `zstd` 命令；普通 `.tar`、`.tar.gz`、`.tar.bz2`、`.tar.xz` 使用 Python 标准库。
- 直接调用使用已安装的工具和当前操作系统身份，收据中的 `project_id` 为 `null`。
- 需要关联已登记项目时，同时传入 `--harness-root` 和 `--project`，读取中央本机项目登记；收据记录该项目标识。

例如，直接预览单文件上传：

```bash
python -m harness.utils.transfer.b2 push --file \
  --local /path/to/workspace/ResearchHarness.tar.zst \
  --remote 'b2:example-bucket/ResearchHarness.tar.zst'
```

远程路径支持空格、中文及普通文件名字符，包含空格的参数使用引号。目标采用
`连接名:存储桶/具体路径`，保留对存储桶内明确文件或目录的选择。

后文 Bash 示例使用可选的上下文数组。直接处理文件时：

```bash
rh_transfer_context=()
```

关联项目时，将数组设置为中央目录和实际所属项目：

```bash
rh_transfer_context=(
  --harness-root /path/to/workspace/ResearchHarness
  --project YOUR_REGISTERED_PROJECT
)
```

Python 调用可以直接使用 `b2.Engine()` 或 `archive.Engine()`。需要在回执上关联项目时可传入 `project_id`。

本机 rclone 位于 `/usr/bin/rclone`；私有连接配置通常为
`/path/to/user/.config/rclone/rclone.conf`。本机 `b2:` 是现有 B2 远程连接的别名。
其他机器请使用自己的配置。密钥由 rclone 私有连接配置管理，管理代码及收据使用连接别名和操作结果。

## 按指定范围下载目录

`pull` 保留源目录内的相对结构，使用 `rclone copy --immutable`。
匹配的已有文件会跳过；已有文件内容冲突时会报错并保留原文件，目标中的额外文件也予以保留。

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  pull --remote b2:example-bucket/projects/SpatialPheno \
  --local /path/to/workspace/SpatialPheno \
  --exclude '/experiment/**' --exclude '/extract_embedding/**' \
  --exclude '/old_project/**'
```

确认预览后追加 `--execute`。可以重复传入 `--include` 和 `--exclude`；规则使用
rclone 的筛选规则，以 `/` 开头表示相对于传输根目录。例如：

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  pull --remote b2:example-bucket/projects/SpatialPheno/experiment \
  --local /path/to/workspace/SpatialPheno/experiment \
  --execute --receipt /path/to/workspace/receipts/experiment-copy-001.json
```

`push` 交换本地与远程方向。远程地址必须定位到存储桶内的具体目录或文件。
执行时先打印开始记录，结束后打印包含状态、退出码、耗时和结束时间的完整结果；
指定 `--receipt` 时，相同最终结果同时写入收据。
失败或受阻时，`diagnostics` 保存实际错误原因、对本次任务的影响和下一步建议。
例如缺少 rclone 时，收据说明传输程序尚未启动，并提示安装工具或修正 PATH 后重试；
文件冲突时，收据说明目标保持原样，并提示选择新的目标位置。程序错误输出的末尾随记录保存。

## 单独下载一个文件

加 `--file` 选择一个文件，`--local` 必须是完整目标文件名：

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  pull --file --remote b2:example-bucket/zipped/data.tar.zst \
  --local /path/to/workspace/data.tar.zst --streams 8 \
  --execute --receipt /path/to/workspace/receipts/data-copy-001.json
```

单文件执行先使用 rclone 的传输预览判断已有目标是否冲突；冲突时返回失败并保留目标。
实际复制采用 `copyto --ignore-existing` 保留已有文件。这个步骤补足本机 rclone
单文件 `copyto --immutable` 未阻止冲突覆盖的行为，使用传输自身的比较方式，
额外 `verify` 和独立 SHA256 核验继续按人类要求执行。
重新执行会跳过已经匹配的文件。传输中断的大文件可能从头重新下载，续传行为取决于实际传输结果。

默认参数：同时传输 16 个文件、同时核对 16 个文件、每个文件使用 4 条传输连接；
文件达到 256M 时启用多线程，每块 64M；启用快速列表，重试 10 次、底层重试 20 次，连接超时 15 秒、请求超时 5 分钟、重试间隔 10 秒。
通过 `--transfers`、`--checkers`、`--streams`、`--chunk-size`、`--cutoff`、`--retries`、
`--low-level-retries`、`--connect-timeout`、`--timeout`、`--retries-sleep` 和
`--no-fast-list` 调整。并发的合适值需要按带宽、内存与文件分布测试。

## 人类明确要求或审核批准后的额外校验

以下 `verify` 操作用于人类明确要求或审核批准的核验。上传、下载完成后按实际传输结果报告，
额外校验默认保持未执行。

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  verify --local /path/to/workspace/SpatialPheno/experiment \
  --remote b2:example-bucket/projects/SpatialPheno/experiment \
  --execute --receipt /path/to/workspace/receipts/experiment-check-001.json
```

`verify` 是单向 `rclone check`，要求本地选中文件在远程存在且匹配；远程可保留额外文件。
筛选下载后，校验时使用相同的纳入与排除参数（`--include` 和 `--exclude`）。单文件校验加 `--file`，本地与远程文件名必须相同。
rclone 使用存储服务支持的文件摘要或文件属性。人类明确要求或审核批准独立 SHA256 核验时，
按该次指定范围另行计算或维护清单。
收据仅在 `verify` 实际成功后标记 `remote_integrity=CHECKED`，普通传输记录为 `NOT_RUN`；
传输结果、额外核验结果及科研结论分别按实际依据报告。

## 查看压缩包中的选定内容

```bash
python -m harness.utils.transfer.archive "${rh_transfer_context[@]}" \
  list --archive /path/to/workspace/data.tar.zst \
  --include data/SpatialPheno_datasets --execute
```

`list --execute` 以只读方式列出选中内容，处理过程需要顺序解压扫描 tar 压缩流。
默认预览仅打印参数；包内目标的实际存在情况由带 `--execute` 的读取操作确认。

## 只解压一个目录

```bash
python -m harness.utils.transfer.archive "${rh_transfer_context[@]}" \
  extract --archive /path/to/workspace/data.tar.zst \
  --destination /path/to/workspace/data/SpatialPheno_datasets \
  --include data/SpatialPheno_datasets --strip-components 2 \
  --execute --receipt /path/to/workspace/receipts/dataset-extract-001.json
```

这里 `--strip-components 2` 去掉 `data/SpatialPheno_datasets/`：
`data/SpatialPheno_datasets/mouseAD/example.h5ad` 会写入
`/path/to/workspace/data/SpatialPheno_datasets/mouseAD/example.h5ad`。
目标必须使用新的目录路径；目标路径已占用时，工具拒绝该次提取并保留已有目录。

其他选择方式：

```bash
# 一个文件：通过 include 指定目标
--include data/SpatialPheno_datasets/mouseAD/example.h5ad

# 多个目录或文件
--include data/project_a --include data/project_b

# 所有 h5ad，并排除缓存目录
--include '*.h5ad' --exclude '*/cache/*'
```

解压筛选匹配完整包内路径；指定目录名时自动包含其中的文件和子目录，通配符按 Python fnmatch 规则匹配，
`*` 可以跨越 `/`。默认区分大小写；`--ignore-case` 可忽略。rclone 的传输筛选按前文说明的规则处理。

- `--reserve-gib 2`：默认保留 2 GiB，写每个文件前检查空间。
- `--progress-interval 20`：每 20 秒打印扫描进度；设为 0 关闭周期进度。
- 普通提取记录文件路径和字节数。人类明确要求文件摘要时，添加 `--sha256`，边写边计算并将摘要保存到返回结果及可选 JSON 收据中；Python 接口采用 `sha256=True`。
  摘要提供文件身份；与外部清单比较按人类指定的核验任务执行。
- 只支持普通文件与目录；选中的符号链接、硬链接、设备等特殊项会拒绝。
- 拒绝越界路径、输出路径冲突、已有目标和解码错误。先提取到目标父目录内的临时目录，
  成功扫描并通过解码器检查后再改为正式目录名。
- 失败默认清理本次临时目录；`--keep-partial` 会保留它并打印路径，供人工检查。
  保留的目录用于人工检查；再次提取仍按完整提取流程处理。
- 原压缩包保留，磁盘输出范围限于筛选选中的目录和文件。依赖顺序访问的 `.tar.zst` 仍需顺序扫描，
  选择性提取节省输出空间，扫描时间和远程下载流量取决于实际扫描与传输过程。

所有收据使用新路径，已有收据保留原文。命令成功、数据一致性和科学复现分别按各自依据报告。

## 可选的工具检查

工具检查作为按需选择的操作，仅在用户明确要求时执行 `python -m pytest -q tests/test_transfer.py`。该测试使用本地合成文件和临时的本地目录连接，连接范围限于本地测试资源。


## 整体与子功能

本目录以实际文件处理对象区分两种工具，共同服务于用户明确要求的数据搬运。

| 局部条目 | 完整子功能 | 如何服务整体 |
| --- | --- | --- |
| `__init__.py` | 声明传输包。 | 提供传输工具的模块导入入口。 |
| `b2.py` | 预览或执行 rclone 下载、上传和核对。 | 把选定连接中的文件搬运到指定位置。 |
| `archive.py` | 预览 tar 成员并按明确路径选择性解压。 | 把压缩资料安全展开为指定输出。 |
