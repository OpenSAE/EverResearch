# Data transfer, validation and compression package decompression

## Purpose

This document describes how to access the B2/rclone download, upload and verify tool for ResearchHarness, and the viewing and depressure tool for tar compression packages. It specifies the default clean-up method for downloading and package uploading, and provides examples of operations.

## Scope

Read when the user specifically requests the use of ResearchHarness to transmit, verify, view or depress the file, or the task involves the modification of the transfer and depressure program in `utils/transfer/`.

## Two tools

| Access. | Actual use |
| --- | --- |
| `python -m harness.utils.transfer.b2` | Download, upload or check files via the configured remote connection in rclone |
| `python -m harness.utils.transfer.archive` | View local tar content and filter the extract file by path |

The above commands are only previewed; `--execute` is added to try to be practical. Both modules can directly handle the specified file. Examples of commands are used to explain parameters, and actual transfers or decompressions are performed with the express authorization of the user.

B2 Ordinary uploads and downloads are performed using rcline's own transmission check to record the completion of the actual transmission results.
Additional `verify` validation and independent SHA256 summary list only after explicit human request or approval.
The assistant arranges for these additional verifications on the basis of current human instructions, and the routine transmissions do not require a check-in procedure; the receipt is properly recorded and executed.

## Default decompression after downloading tar package and cleaning

When the user requests to download a single tar compression package, the assistant defaults to deliver the complete decompression and clean the package that is being downloaded as the same. The user specifies that only downloads, retains the compressor package or select decompression will be handled within the specified range.

1. After the download is successful, the full decompression is judged from the space available in the file system where the extended size of the package member and the target are located. The default value of the extraction tool is set at 2 GiB, and the specified value is used when the user assigns other residuals. When space is sufficient, the full decompression is used in the new directory and waits for the tool to report success. Priority is given to the user-defined decompression directory, while the rest uses the new directory next to the compressed package and corresponding to the package name, keeping the inside structure clear.
2. When a complete decompression is successful and the official result is set, delete the local compression package that is being downloaded and report on the decompression directory. Use the already existing package to decide whether to clean it according to the user's instructions to the file.
3. If the space is insufficient, the target exists or the full decompression fails, keep the local compression package, indicating the actual reason and the document currently available. Selective decompression retains the package.

## Pack directory upload to B2 and clear tar by default

When the user requests that a local directory be packaged for upload, the assistant defaults to remove the temporary tar package generated after the upload has been successful and to keep the local source directory. Before processing, the user is asked whether to keep the source directory or to remove it after upload has been successfully to release the space. The user has clearly chosen to follow this decision. When a response has not been received, the package and upload can be completed as authorized, and the source directory is maintained by default.

1. Creates a tar package for this upload outside the source directory and uploads the complete package as a single file to the specified B2 path.
2. Clears the temporary tar package after uploading successfully. The source directory is deleted only if the user expressly chooses to delete the source directory and confirms that the directory still corresponds to the upload contents. When the directory is packed, the directory is maintained and the actual changes are reported.
3. Retains the source directory and the already fully generated local package when packing or uploading failed, so that you can try again. Report on the status of remote upload, and the actual removal of the local package and source directory.

## Maintenance of transmission and decompression function

When a functional change is made, the user is selected how to obtain and use the document, and how to continue after failure, then the order, result and receipt are arranged. Recording the relevant source, target and range; and, if failure or obstruction occurs, retain the actual error, target processing and the next recommendation that applies. Using the local document scene, read the document and receipt through the public entry point, confirm that the result can be used for the original operation, retesting or conflict management.

## Preconditions and optional item records

- Python 3.11/3.12, Research Harness installed.
- Uploading, downloading and additional verifications require the installation of `rclone` and pre-established remote connections using the B2 native interface in the caller's private configuration.
- `.tar.zst` / `.tar.zstd` decompression requires `zstd` command; normal `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz` uses the Python Standard Library.
- Directly calls the installed tool and current operating system identity, `project_id` in the receipt `null`.
- If a registered project is required to be connected, it is also `--harness-root` and `--project` to read the central owner project registration; receipts record the project identifier.

For example, direct preview list files are uploaded:

```bash
python -m harness.utils.transfer.b2 push --file \
  --local /path/to/ResearchHarness.tar.zst \
  --remote 'b2:example-bucket/ResearchHarness.tar.zst'
```

Remote path supports spaces, Chinese and normal filename characters, using quotation marks for parameters that contain spaces.
`connection:bucket/path`, retain the option of specifying the file or directory in the drum.

Later on, for example, Bash uses the optional context array. When directly processing a file:

```bash
rh_transfer_context=()
```

When linking items, set the array to a central directory and the actual item to which the item belongs:

```bash
rh_transfer_context=(
  --harness-root /path/to/ResearchHarness
  --project YOUR_REGISTERED_PROJECT
)
```

Python calls can be used directly at `b2.Engine()` or `archive.Engine()`. You need to upload `project_id` to the associated item on your reply.

Use `rclone config file` to find the private configuration for the current user.
The examples use `b2:` as a placeholder for your own configured remote alias.

## Download directory by specified range

`pull` Retains the relative structure in the source directory, using `rclone copy --immutable`.
Matches an existing file that skips; errors are reported and the original document is kept when the content of the existing document is conflicting, and the additional document in the target is retained.

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  pull --remote b2:example-bucket/projects/BirdStudy \
  --local /path/to/BirdStudy \
  --exclude '/experiment/**' --exclude '/tmp/**' \
  --exclude '/old_project/**'
```

Confirms the preview by adding `--execute`. You can repeat `--include` and `--exclude`; the rules are used
rclone's filter rules begin with `/` as opposed to the transfer root directory. For example:

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  pull --remote b2:example-bucket/projects/BirdStudy/experiment \
  --local /path/to/BirdStudy/experiment \
  --execute --receipt /path/to/receipts/experiment-copy-001.json
```

`push` Exchanges local and remote directions. Remote addresses must be located in a specific directory or file in a storage drum.
Prints the beginning of the record at the time of execution, after which the complete results of the state, exit code, time-consuming and end time are printed;
When `--receipt` is specified, the same final result is included in the receipt.
In case of failure or obstruction, `diagnostics` saves the cause of the actual error, the impact on the mandate and the recommendations for the next step.
For example, when rclone is missing, the receipt indicates that the transfer program has not been started and suggests that a tool be installed or that PATH be modified to try again;
When a document is in conflict, the receipt indicates that the target remains as it is and suggests that a new target position is selected. The end of the error is saved with the record.

## Download a file alone

Add `--file` to select a file, `--local` must be the full target file name:

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  pull --file --remote b2:example-bucket/zipped/data.tar.zst \
  --local /path/to/data.tar.zst --streams 8 \
  --execute --receipt /path/to/receipts/data-copy-001.json
```

Single file executes a transmission preview first using rclone to determine whether an existing target is in conflict; returns in conflict and retains the target.
The actual copy uses `copyto --ignore-existing` to keep the existing document. This step is to fill the rcline
The single file `copyto --immutable` does not prevent conflict-covered behavior, using a way to transmit its own comparison,
Additional `verify` and independent SHA256 verifications continue to be carried out in accordance with human requirements.
Re-executing skips a matching file. Large files that are interrupted may be downloaded from the top, and the continuation will depend on the actual transmission result.

Default parameter: transmit 16 files simultaneously, check 16 files at the same time, using 4 transfers per file;
Enables multiple threads at 256M, 64M each block; Enables a fast list, retrying 10 times, retrying 20 times at the bottom, connecting 15 seconds, requesting 5 minutes and 10 seconds between retrying.
Through `--transfers`, `--checkers`, `--streams`, `--chunk-size`, `--cutoff`, `--retries`,
`--low-level-retries`,`--connect-timeout`,`--timeout`,`--retries-sleep` and
`--no-fast-list` adjusts. The appropriate value for simultaneous distribution needs to be tested by bandwidth, memory and file distribution.

## Additional verification required or approved by humans explicitly

The following `verify` operation is used for humans to explicitly request or verify approvals.
Additional verification defaults remain unexecuted.

```bash
python -m harness.utils.transfer.b2 "${rh_transfer_context[@]}" \
  verify --local /path/to/BirdStudy/experiment \
  --remote b2:example-bucket/projects/BirdStudy/experiment \
  --execute --receipt /path/to/receipts/experiment-check-001.json
```

`verify` is a one-way `rclone check` , requiring local selected files to be available and matched remotely; remotes can save additional files.
After filtering downloads, verify using the same inclusion and exclusion parameters(`--include` and `--exclude`).Check-up of single files `--file`,Local and remote filenames must be the same.
rclone uses a file summary or file attribute supported by a storage service. When humans explicitly request or verify the approval of an independent SHA256, you can find a file that you want to verify.
The list is calculated or maintained separately from that assigned range.
The receipt is only for... `verify` Mark after actual success `remote_integrity=CHECKED`,Normal Transfer Record As `NOT_RUN`;
The transmission results, additional verification results and scientific findings are reported on a factual basis.

## View the selected contents in the compression package

```bash
python -m harness.utils.transfer.archive "${rh_transfer_context[@]}" \
  list --archive /path/to/data.tar.zst \
  --include data/example_dataset --execute
```

`list --execute` lists the selected content in read-only format, and the process requires a sequentially decompressed scan of the tar compression stream.
The default preview is only printed parameters; the actual existence of the target in the package is confirmed by a reading operation with `--execute`.

## Only one directory to decompress

```bash
python -m harness.utils.transfer.archive "${rh_transfer_context[@]}" \
  extract --archive /path/to/data.tar.zst \
  --destination /path/to/data/example_dataset \
  --include data/example_dataset --strip-components 2 \
  --execute --receipt /path/to/receipts/dataset-extract-001.json
```

Here. `--strip-components 2` Get rid of it. `data/example_dataset/`:
`data/example_dataset/sample/example.h5ad` will write
`/path/to/data/example_dataset/sample/example.h5ad`.
The target must use a new directory path; when the target path is occupied, the tool rejects the extraction and retains the existing directory.

Other options:

```bash
# One document: adopted include Specify Target
--include data/example_dataset/sample/example.h5ad

# Multiple directories or files
--include data/project_a --include data/project_b

# All h5ad,And exclude cache directories
--include '*.h5ad' --exclude '*/cache/*'
```

The depress screen matches the path in the complete package; the file and subdirectories are automatically included when the name of the directory is specified, and the wildcards match by the Python {\fnmatch) rule.
`*` You can cross `/`. Default case-sensitive; `--ignore-case` is negligible. rcline's transmission filters follow the rules described above.

- `--reserve-gib 2`: Default to keep 2 GiB to check space before writing each file.
- `--progress-interval 20`: Print scan progress per 20 seconds; set to 0 for closure cycle progress.
- Normally extracts the path and bytes of a record file. When a human specifically requests a file summary, add `--sha256`,Write-by-Calculate and save summary to return result and optional JSON In receipt; Python Interface implementation `sha256=True`.
  The summary provides an identity of the document; it is performed in accordance with a human-designated verification mission compared with the external list.
- Only normal files and directories are supported; the selected symbol links, hard links, devices, etc. will be rejected.
- Refuses to cross-border routes, exit paths conflict, and has a target and decode error. First, access to a temporary directory in the target parent directory.
  Successfully scanned and checked through a decoding device before changing to an official directory name.
- Failed to by default clear this temporary directory; `--keep-partial` will keep it and print the path for manual inspection.
  The maintained catalogue is used for manual check-ups; re-extracting is still processed in a complete extraction process.
- Keeps the original compression package while executing the extraction command separately. The cleanup of the full decompression after downloading is executed by this document "Default decompression after downloading the tar package". The disk output is limited to filtering the selected directory and file. The `.tar.zst` in the order of access still needs to be scanned in sequence.
  Selective extraction saves output space, and scanning time and remote download traffic depend on the actual scanning and transmission process.

All receipts use a new path and are kept in their original language.

## Optional tool check

The tool check is selected as a needs-based operation, only `python -m pytest -q src/harness/utils/transfer/test_transfer.py` if the user so requests. This test uses local synthetic files and temporary local directory connections, which are limited to local testing resources.


## Whole & Sub function

The catalogue distinguishes two tools from actual document-processing objects, serving jointly the data removal specifically requested by the user.

| Local entries | Full sub-function | How to serve the whole |
| --- | --- | --- |
| `__init__.py` | Declare the transfer package. | The module import portal that provides the transfer tool. |
| `b2.py` | Preview or execute rclone download, upload and check. | Moves the selected connection file to a given location. |
| `archive.py` | Preview of the tar members and selective decompression according to a clear path. | Expands the compressed information security as the specified output. |
