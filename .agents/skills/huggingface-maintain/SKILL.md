---
name: huggingface-maintain
description: Visits and maintenance Hugging Face Account number, Spaces with the data set repository. Use to view the login identity and the warehouse, upload or update the data set and Space File, maintenance description, viewing status, restart or pause Space,And configure environment variables and keys.
---

# Hugging Face Access and Maintenance

## Purpose

Use the Hugging Face official command and the Python client to access user accounts and maintain clearly specified Spaces and data sets. Put user requests in natural languages into repository reading, file submission, running status query and specified maintenance operations.

## Scope

The user requests to view the Hugging Face login identity, warehouse and file, create or update datasets and space, download the specified content, or manage the Space run and configuration. The target is determined by the account number or organization, the full repository name, the repository type, the file range and the operation. Modelling training, reasoning service deployment and data processing are handled according to the user's individual task.

## Tools and accounts

- Use installed `hf` Orders and `huggingface_hub` Python Package. First look at the help or method signature of the machine's command, using the interface that the current version actually supports.[Command description](https://huggingface.co/docs/huggingface_hub/en/guides/cli)Understanding access and file operations, reference [Space Management note](https://huggingface.co/docs/huggingface_hub/en/guides/manage-spaces)Know how to run and configure.
- Use `hf auth whoami` to confirm the current login identity. Python uses `HfApi()` to reuse the existing login or `HF_TOKEN` environment variable. The account number and organization are determined from the current identity and user-specified target, and the entire skill can be moved with the folder.
- When login is required, direct users to use `hf auth login` at their own terminals, or configure `HF_TOKEN` through a certificate entry to the operating environment. The tokens, space keys and complete authentication responses are kept at the certificate processing point; dialogue, command parameters, drafts and logbooks only record identity, key names and operational results.
- The user designates the organization's warehouse, using the full name of the organization.

## Make the request operational

1. Determines the object: The complete repository name is `owner/repository`; the type is `dataset`, `space` or `model`. The file operation also determines the local source, the remote relative path, and the branch specified by the user.
2. Query for existing status: Read the target repository information, list of documents and, if necessary, description or Space configuration. Clear name, type, public or private when building a new warehouse; New Space also determines the static page, Gradio or Docker type.
3. When the user has identified the objectives and operations, the task within the mandate is done directly. Ask the item if the key information that will change the objective or effect is missing. Delete the remote content, change visibility, expand the upload range or increase the paid resources, each on the basis of the user's express request.
4. Prepare an internal copy before upload to see the actual document to be submitted and the corresponding remote content. Execute new and updated in accordance with the current request; remove at the remote end the execution based on the explicitly selected deletion range.
5. Report the actual submission, download location or state of operation, providing a repository or Space link. Submit a report on the return success and application readiness separately; the query status is used for a limited number of times and still indicates the current status at the time of construction.

## Local data and upload copy

This skills directory is currently available `SKILL.md` location is determined. Use an internal directory every time information is generated `results/<Use and time or other marking>/`,Save as required `staging/` Upload copy,`downloads/` Download content, cache and operation records.

Uploads from a user-selected directory or file to `staging/` to submit an internal copy. The original file content is consistent with the selection; the original input is read-only. When new descriptions, changes to the dataset card, directories or additions to the Space configuration are required, the internal copy is processed in accordance with this request. Clarify the correspondence of the local file to the remote relative path and display only a summary of the changes necessary before submitting.

Identifys the actual target of the symbol link when copying; the link points to the content outside the selected range, specifying the actual object after transfer. Uploading uses the selected file collection and leaves the certificate, the preparation log and the cache in their respective directories.

## Download Droppoint & Cache

- **Normal Hub Download.** Check the current interpreter. Hugging Face Cache Settings. The default root directory is `~/.cache/huggingface`,Settings `XDG_CACHE_HOME` Period `$XDG_CACHE_HOME/huggingface`,Remarkable. `HF_HOME` Priority. Hub,Xet and Datasets The default for processing the cache is under this root. `hub/`,`xet/` and `datasets/`,It can be passed separately. `HF_HUB_CACHE`,`HF_XET_CACHE`,`HF_DATASETS_CACHE` Overwrite. Use `local_dir` You can directly specify the destination directory of the downloaded file. The path is determined before importing the client or starting the sub-process, and the existing authentication location is maintained..[Hub Environmental variables](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables) · [Download File](https://huggingface.co/docs/huggingface_hub/en/guides/download) · [Datasets Cache](https://huggingface.co/docs/datasets/en/cache)
- **Skills Tasks.** A visible selection of an internal download directory, and a repository that maintains a copy of the download entry using this skill. Sets an independent task Hub,Xet Cache and a temporary directory of the process to facilitate the understanding of the actual drop point and the continuation of recovery. When a single file is read-only or delivered directly, use the actually needed official download entry.
- The **project is officially entered.** is a permanent location and source version of the project registration.

Each job catalogue uses `log_updates.jsonl` to record new or updated local products: time-bound, skills-based relative paths, brief content, physical source tools or documents. Remote operation records repository, type, file range, submission identification or operational status; key operations only record name and success.

### Download existing assets and create a local job directory

When the user requests to download or create a local copy of the warehouse, use `scripts/download_assets.py` for this skill. It downloads all submitted warehouse files from the official client to organize the local directory by account number or organization, warehouse type and warehouse name.

```text
results/<run ID>/
├── inventory.json
├── log_updates.jsonl
├── cache/
├── tmp/
└── <Account number or organization>/
    └── spaces/,datasets/ or models/
        └── <Warehouse Name>/
            ├── repository.json
            ├── source/
            └── checkout/
```

`source/` Saves the original file of this regular submission, `checkout/` is an independent maintenance copy, both of which maintain the original file structure in the warehouse. `repository.json` Records remote address, warehouse type, submission version, and list of documents. The subsequent editing takes place at `checkout/`, uploading the selected job content for copying to `staging/`. Creates a new named task when the remote source is updated, and maintains the existing version and local changes.

Replace `<skill-directory>` with the full skill path and repeat `--repo` in this actual range:

```bash
python <skill-directory>/scripts/download_assets.py --task <run ID> \
  --repo space:<Account number or organization>/<Warehouse Name> \
  --repo dataset:<Account number or organization>/<Data set name>
```

After the normal web download has been interrupted, the same taskname, the same warehouse list and `--resume` continue to be downloaded in a fixed version. The program continues by the continuous phase of downloading, source copy, working copy and warehouse record: copying is completed in the name ' s temporary directory and then the entire body becomes an official copy. Repossessing the existing working copy and local editor; existing source copies of the old task are checked with the fixed version and continue to generate missing working copies when the content is consistent. Local copies are kept for the repository file and source submission, Git history, Space service interface key and running disk information, respectively, according to the additional range suggested by the user.

## Common Operations

The Python operation begins with the official client below; the name and path in the example is replaced by the actual value of the current task. The example is used to select the task to be called, create, upload, suspend and configure the respective user request.

```python
from huggingface_hub import HfApi, hf_hub_download

api = HfApi()
```

### Read account number resources and warehouses

```python
# namespace From current account number or user-designated organization; increase number of returns as needed.
datasets = [item.id for item in api.list_datasets(author=namespace, limit=20)]
spaces = [item.id for item in api.list_spaces(author=namespace, limit=20)]
info = api.repo_info(repo_id=repo_id, repo_type=repo_type)
files = api.list_repo_files(repo_id=repo_id, repo_type=repo_type)
```

Read the selected file as needed, using a specified download location. The data set downloads are maintained at `repo_type="dataset"`, the Space file at `repo_type="space"`.

```python
path = hf_hub_download(
    repo_id=repo_id, repo_type=repo_type,
    filename=remote_path, local_dir=download_directory,
)
```

### Create, upload and update data sets

```python
url = api.create_repo(repo_id=repo_id, repo_type="dataset", private=private)
commit = api.upload_folder(
    repo_id=repo_id, repo_type="dataset", folder_path=staging_directory,
    path_in_repo=remote_directory, commit_message=message,
)
```

The single file is updated with `api.upload_file(path_or_fileobj=staged_file, path_in_repo=remote_path, repo_id=repo_id, repo_type="dataset", commit_message=message)`. When the data set card is updated, `README.md` is used as the actually selected upload file. The user's data format, partitioning and permission are maintained; this information is completed on the basis of actual information if additional information is required.

### Create, update and run Space

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

Space code, relying on the application type and access configuration in `README.md`. Restarting `api.restart_space(repo_id=repo_id)`, suspending `api.pause_space(repo_id=repo_id)`, suspending normal restarts from suspending. Hardware, storage and other charge settings are handled in accordance with clearly specified resource requirements.

### Set Variables and Keys

Normal configuration calls `api.add_space_variable(repo_id=repo_id, key=key, value=value)`. The key is read from the user-specified certificate entry or environment variable, and then calls `api.add_space_secret(repo_id=repo_id, key=key, value=secret_value)`. After completion, report the name and operational status of the report, and the configuration change may trigger Space restart and then query the actual operational status.

## Common Results Processing

- If the authentication fails, confirm the current source of the certificate and guide the re-entry; check the type of warehouse, the full name and the scope of the certificate if the authority is insufficient.
- When the warehouse is not located, the actual visit results are stated in combination with the name of the login and the target; the access capacity of the private warehouse is based on the return of the service.
- When documents are larger or larger, the official large catalogue upload capability is selected on a physical scale, and the preparation of copies and caches continues to be kept in this skill.
- If the network interrupts or the writing results are not known, read the remote file or state of submission before deciding whether to try again. Read the current version again when a conflict is submitted, and you can consolidate the contents according to the range of changes determined by the user and continue; specify the differences and options when the conflicting content is selected.
- The failure report retains the required status code and reason; the key value and the address with authentication information are removed before the output.

## Development inspection

When you change the download program, run `python tests/test_download.py` with a clear test range. It checks local client back-to-back copies of sources, working copies and warehouse records, and check that the edit is maintained. Real account access and network downloads are executed with the resources selected by the corresponding task.
