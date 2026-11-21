# Preparation, publication and preservation

## Purpose

Describe the order, scope of the document, internal copy, differences and method of saving the results of the release procedure.

Information is also provided on how local and GitHub comparisons are prepared within the skills, covering the collection of documents on both sides and recording discrepancies.

## Scope

This document is used to execute a copy of a directory or file, to publish a warehouse, to merge a request (PR), to release a package or version (Release). This document is used by a smart assistant to call an internal program and communicates with a user in a functional language in SKILL.md.

This document is also used when comparing GitHub projects with local skills, preparing for comparison of copies and viewing differences.

## Internal realization and operating conditions

`../scripts/publish.py` is the entry point for the program to release the preparation, delivery and version operation, using only the standard library of Python 3.11 and above, to call the installed Git and GitHub command lines. The description and scripts in the stand-alone folder complete the process; the program is located at its own location `results/` and is still operational when it moves as a whole. The first download of a long-term project uses standard Git, creating a shallow cloning of the current branch within the skills `projects/<project-name>/repo/`, accompanied by a description to be kept in the same project directory; a copy is subsequently published as a reading source for `prepare`.

The repository operation is `owner/name` for GitHub.com. The login is read from the current machine and can also be used in the environment `GH_TOKEN` or `GITHUB_TOKEN`. The program points to the task with the configuration of the GitHub command line entry and the temporary and cache position of the tool.

Replace `<Skilldirectory>` with the complete absolute path of the current directory `SKILL.md` in the command. Below is a structural example of which the source, repository, branch and author are filled out by the real task.

## Check how it works

Press first. `SKILL.md` Determine local absolute path, file range for each item, GitHub Repository, version, repository subdirectories and paths. Use the current task to create new ones `results/<run ID>/`,Save Internal:

- `local/`: Select a separate copy of the local document.
- `remote-checkout/`: Specifies a read copy of the GitHub repository.
- `remote/`: Copies of GitHub files organized in the same range and path.
- `comparison.json`: Local sources, scope, path matching, remote branching and actual submission, as well as list of documents and comparison results on both sides.
- `comparison.diff`: Difference between text and document.

Copy local path files to a defined range `local/`.passed Git Read specified repository and version in `remote-checkout/` from which the actual submission is obtained and copied from the corresponding directory by the same trade-off to `remote/`.Work directories, temporary files and caches of all tools to use the internal location of the task; call Git This is how you use the release process to isolate the source warehouse from the internal operation and authenticate the login. The task information is kept as it is and the result is written in the new task directory.

Compares the full list of documents and actual contents of two copies and maintains the enforceable attributes that need to be delivered. First, you identify unique files on both sides by path, then compare shared files; empty directories are recorded in the actual directory structure. Text differences can be saved in the task directory using the following standard Git command:

```bash
git diff --no-index --binary --no-ext-diff --no-textconv -- local remote > comparison.diff
```

This command exits with the same number as 0, and indicates a difference for 1; other exit codes indicate an error in the operation and need to report the actual extent of completion once the cause has been identified. `comparison.json` and `comparison.diff` records the time, relative path, content and actual source within the mission through `log_updates.jsonl`. Read failure or file changes during copying, specify the specific object, and continue to compare after retrieving the corresponding content.

In the end, the user is asked to decide whether or not to align and align the actual file differences and uses. After the user has chosen to update GitHub, the user calls `prepare` below to prepare the corresponding release; GitHub's unique file is deleted to fill `--delete` according to the specific path approved by the user. When the user chooses to adjust the local location, the internal copy is prepared to select the changes and display the differences, and the actual changes in the original directory are processed according to the target item maintenance process.

## Scope of preparation documents

`prepare` Reads only sources and remote warehouses, copying, preparing differences within skills, and actually creating warehouses, push-off, PR and Release are implemented in subsequent independent orders.

```bash
python <Skill Contents>/scripts/publish.py prepare \
  --root /path/to/workspace/ResearchHarness \
  --map .agents/skills/extract-structure=. \
  --exclude .agents/skills/extract-structure/results \
  --repo OWNER/extract-structure \
  --new --visibility private
```

`--map source=destination` Repeatable. Source relative to `--root`, target relative to destination repository root directory:

- Catalogue map to `.`: Place the contents of this directory in the repository root directory.
- Directory map to `tools/environment`: Keeps the internal structure of the directory and places it at that location.
- The file is map to `tools/probe.py`: Place the file on this specific path. Use the original filename when a single file is map to `.`.
- Multiple maps stop when the same name or file conflicts with the directory, and the source file is kept.

`--exclude` Repetitively, use a path or wildcard relative to the root source directory. Path matching is excluded with its subdirectories. The file selects whether the product, the in-house configuration and the temporary catalogue are included in the map and exclusion, as determined by the user, and implemented in the map and exclusion parameters; `.gitignore` File Ignore Settings for Git.

Call `prepare` First, press first. SKILL.md "Pre-Scanning, Description and Selection" to perform a read-only scan showing the use of the main directory, the number of files, the size and historical information, the results, the cache, etc., and obtain a range selection after the current round of scans. Only the same is done when a temporary local warehouse or version package is prepared; the user requests the entire directory in general terms to show the scan results and ask once. Git Repository. The sequence is executed by the skill workflow.,`prepare` The command itself follows the existing parameter interface. The user 's decision is written in `--map` and `--exclude`;The exclusions in the list of commands are used only for demonstration, which is the decision of the current user. The program itself is copied to a given range, and the file category and its use is judged by the smart assistant reading it.

In the current task, the scope of the ZIP attachment is consistent with the selection in `source/`. If the user wishes the repository to use a different range from the attachment, separate `prepare` and `pack` for the attachment scope, all files remain within this skill; the scope of the GitHub home-based source package is clearly specified when the package is uploaded at the entry point of the GitHub command line. The information in the warehouse is defaulted to remain and the target file is included in the approved range `--delete` when removed from the warehouse. The scope of the GitHub home-bound source package is determined by the entire warehouse with the label.

The program always omits Git metadata. The parent directory containing this skill is omitted from `results/`; it can be included when a given product is clearly selected as a source. Symbolic links and special files report their location and stop, and the user can switch to the actual file; independent copies are copied with a normal file. Git and ZIP versions of the package are delivered in units of the actual document, with the directory structure maintained by the file.

`--new` indicates that the user explicitly requests a new warehouse with a combination of `--visibility private` or `public`. The default branch is `main`; when other branches are actually used, `--base`. This step is prepared locally; a remote repository is created in subsequent release steps.

There are examples of warehouses:

```bash
python <Skill Contents>/scripts/publish.py prepare \
  --root /path/to/workspace/ResearchHarness \
  --map src/harness/utils/probe.py=tools/probe.py \
  --repo OWNER/research-tools \
  --base main --branch publish-environment
```

`--base` is the readable remote base branch. `--branch` omits directly to update the base branch; when new branches are used, a PR can be created at the time of publication. The target new branch stops when it already exists; this already existing branch is to be updated directly, using the same `--base` and `--branch` or choose another new branch.

`--delete target-file-path` is only used when the user expressly requests to delete the target file and can repeat it. Default to keep the rest of the file in the target repository. Deleting objects is specific to the tracking file; directory clean-up lists specific files and then uploads them to the approval range.

Only local copies and version packages can be made by omitting `--repo` and then using `pack`. It still uses the in-house Git repository to save the differences that can be viewed.

## Check the published language

The tape. `--repo` It's... `prepare` Scans the current selected target path and text. Check for direct readable UTF-8 Text, and bytes marked UTF-16 and UTF-32 text. Report `language-check.json` Record the path and line numbers of the Han characters, the bilingual path of the declaration, and the documents that need to be combined with the format or preview. Pictures, members of the compressed package, transliterated English and English are checked by the release preparation assistant in combination with the format.

Bilingual projects repeat `--bilingual-path` in this range. Use the relative file path in the target repository, or the target directory path at `/`. For example, a bilingual description can be `--bilingual-path README.md --bilingual-path README.zh-CN.md`, stating the English document only when the English description also contains a Chinese toggle label. The program requires that each path match this selected file and that the path saved in the preparation result be published and packaged.

When a problem is detected, the program retains the internal `source/` and the report, and stops before preparing the Git discrepancy. Translator an internal copy of the report and re-executes the `prepare` from that copy.

## View Preparation Results

Commands to return the task identifier, number of files, ignore items, internal copy location and `changes.diff` path. The user is informed of the changes to be published as a result; the internal file is organized as follows:

```text
results/<run ID>/
├── source/              # Independent copy of the selected content of the user, by target path
├── checkout/            # destination repository and its Git Metadata
├── plan.json            # Map files, abstracts, warehouses and branches
├── changes.diff         # Actual prepared Git Variance
├── result.json          # Actual results, generated after execution
├── release/             # Version package, generated as required
├── tmp/                 # Interim information on tools
├── cache/               # Tool Cache
├── config/gh/           # Tool Run Configuration Position
├── hooks/               # Space used for this task Git hooks Location
└── log_updates.jsonl
```

When you read the preparatory results, you use `plan.json` to identify the source and the target path and understand the actual change with `changes.diff`; you determine the location of the completion after the release in the context of `result.json` and the remote physical state. If you fail, you keep this information and locate the reasons within the mandate and continue; if human participation is needed, describe the influence and the implementable options.

The directories are created as required. `plan.json` and `result.json` describe the use and scope of the information with `purpose`, `scope`; log logs record time, relative path within skills, content and program sources. The source directory, its temporary storage area, branch and Git metadata remain as they are.

Only internal copies will be edited when you need to adjust the release. Prepare a new round for updated copies: point `--root` to the round `source/`, use `--map .=.` to repeat parameters such as destination repositorys and branches. Add new instructions, version numbers, etc. to the user's specific authorization, and re-enact new discrepancies.

## Submission and delivery

Call after the user has authorized a specific range:

```bash
python <Skill Contents>/scripts/publish.py publish \
  --run <run ID> \
  --message "Publish selected environment tools"
```

The program uses the current Git author identity; `--author-name` and `--author-email` are provided in the command when required. The identity configuration is used for internal submission, and the user ' s global configuration and source repository is maintained.

The program checks whether the internal copy, content to be submitted and the remote branch are still corresponding to the preparatory results, or stops when a remote writing fails or conflicts occur. It uses a normal push and saves local submission and actual remote operation results. See `result.json` and remote status before re-execution; the same submission is recorded or sent continues.

At this stage, the new warehouse is created using a clear public or private setting; the source content is submitted to the internal warehouse in advance. When the creation is successful but the transmission fails, the created facts are recorded.

## Through PR Delivery

There are warehouses and new branch preparation results available:

```bash
python <Skill Contents>/scripts/publish.py publish \
  --run <run ID> \
  --message "Publish selected environment tools" \
  --pr --title "Add environment tools" \
  --body-file <Skill Contents>/results/<run ID>/pr_description.md
```

First, you write an accurate description inside your skills, `--body-file`, and use the full path. Add `--draft` when you need a draft PR. The program is sent and then you search for the source branch to the open branch of the target base PR; you return the link when you are available and you create it when you are missing. The task of the new repository is to submit a link for the first time and to update the base branch directly.

When creating or renewing the current task, the host uses the attachment tool to attach a real PR link. When the host provides the normal link delivery method, the link returns directly; the release application uses this skill to bring it on its own.

## Version Packages and Release

Create local ZIP only:

```bash
python <Skill Contents>/scripts/publish.py pack --run <run ID>
```

ZIP contains the selected internal copy of the file, the path using the mapd target path. Other files in the target repository and this task record are stored in their original location. The file is stored in the interior `release/` and the file name is marked with the task.

When the user asks GitHub Release to release the content for real submission, then prepare an internal version of the statement:

```bash
python <Skill Contents>/scripts/publish.py release \
  --run <run ID> \
  --tag v0.1.0 --title "ExtractStructure 0.1.0" \
  --notes-file <Skill Contents>/results/<run ID>/version_notes.md
```

Add `--draft` when a draft is required. The program creates a Release and uploads the ZIP for this real-time submission; already available versions of the label must point to the same submission. Existing Release or attachment conflicts will stop and see the actual status before deciding whether to continue.

GitHub downloads its own source code to the entire repository of the label; the ZIP attachments that are uploaded to this skill correspond to this selection. Each of the two downloads is described to the user according to the actual range.

## Post-failure processing and other distribution requirements

Keeps all copies and states after an external operation fails, indicating which of the warehouses that have been created, sent, created, PR or Release are actually completed. Determines how to continue on the basis of `result.json` and remote physical status. Add or delete remote resources, modify the open scope, and enforce branch coverage, as well as build commands for running source projects, as explicitly authorized by the user.

The running entrance provides generic file reproduction, warehouse release, PR, ZIP and Release. Retain the submission history, submodules, Git LFS, automated continuous synchronization and website deployment requirements, explaining the differences from this portal before determining the actual operation; all local writings of the complete process are still in the skills.
