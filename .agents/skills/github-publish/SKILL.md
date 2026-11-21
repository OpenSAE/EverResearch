---
name: github-publish
description: Copy and prepare user-selected content into skills GitHub publishing; comparing local and remote differences; to be selected GitHub The warehouse is downloaded as a fixed item for continuous maintenance.
---

# GitHub Publish — publish selected content to GitHub

## Purpose

Helps the user to post the entire project, a directory or several files to GitHub. First scans the actual directory, describes the content and scope, asks and determines the scope for inclusion, then copys the selected file into this skill, prepares for the changes that can be viewed and completes the release as authorized by the user.

Provides a model for cross-checking: First, determine the local path, GitHub position and range of comparison for each managed project, then explain the differences between the documents and content on both sides for the user to decide whether to align.

Provide long-term project management: download user-selected GitHub repository to `projects/<project-name>/repo/` to maintain current copy and remote correspondence in the fixed project directory.

The original subject is always read-only: the document content and the file collection remain the same. The Git warehouse, the release instructions, the version package, the temporary document and the log are prepared within this skill and are actually sent from inside.

## Scope

The user requests that the selected content be published or updated to the GitHub repository, submitted changes through the consolidation request (PR), or produced and published a version (Release). The user only requests that the project be discussed or viewed with the release change be prepared to that extent.

Users require a control check mode when comparing the GitHub managed project with local skills, to check for differences between the two sides or to discuss alignment.

The long-term project management approach described below is used when users request that GitHub repository be downloaded locally and maintained on an ongoing basis.

Supports GitHub.com. Runs the `gh` entrance to the Python 3.11 and above, Git and GitHub command lines; the warehouse publishes the required GitHub login or a document in the environment. The required job description and program are in this folder. To be published, the item is a reader and GitHub is the user-specified distribution target.

## Presentation of notes

README, statement of differences and publication notes explain directly what the selected content provides, how it is used, and the necessary conditions. Use common terms, complete natural language and positive sentence to expand the technical details according to the needs of the reader.

## Select this way of working

The distribution mode is the following: prepare a copy, display changes and execute the permission to release. The check mode is followed by the local scanning and range selection, “before the warehouse is set up” below, then read out the information and report the differences.

## Long-term project management

Use fixed for each long-term maintenance object `projects/<Project name>/`,Name denotes the actual use.`repo/` Save Current Git A copy of the job, next to it. `project.md` The list of items and the reading portal are available on the list. `projects/README.md`;Each download or update of the product in the corresponding item `log_updates.jsonl` Records.

Read the list of remote documents before the first download, indicating the size, main content and range of the selected document, following the range confirmed by the user after the scan. The complete download uses the light clone of the current default branch, retaining the current full version of the controlled content, the executable properties and the symbol link; the complete history, submodule content and Git LFS entities are arranged according to the user's actual needs. The symbol link is kept as it is and the purpose is explained according to the actual target.

Follow-up maintenance reads the project description and the current Git state, takes existing local changes and user authorizations and then decides to acquire remote content, compare or modify. Long-term working copies within this skill are modified according to the user ' s maintenance authorization; external source directories remain read-only. Releases are prepared from long-term working copies for this stand-alone `results/<run-id>/source/` and `checkout/`, following the distribution process to display specific changes and perform approved operations.

The fixed project directory keeps the object of continuous maintenance; `results/<run-id>/` saves every scan, comparison, release, temporary file and execution record.

## Check Mode

### Clear project path and scope

Each of the projects to be managed identifies the following information, which is documented for this selection, and uses the currently identified target for the actual operation:

- The full absolute path of the local project or skill, as well as the directories and files of this comparison.
- GitHub repository address, branch or version, and corresponding directory in the warehouse. The branch is user-selected; when the user only provides the warehouse, the current default branch of the warehouse is used and the actual selection is specified.
- Local trajectories to GitHub, e.g. local skill directories to store root directories.
- Includes and omits content, such as whether to compare `results/`, caches, historical information, and README and license only added to the release copy.

Read the existing task logs and the current directory, find the true path and the existing correspondence, and then focus on the missing information for impact comparisons. When the user requests to load skills or to be prepared to manage the project, the path and scope are clearly defined; then the comparison needs to be understood when the two sides are consistent.

### Comparison and description of differences

Copy this selected local file inside the skills and read a specified version of GitHub in the same task. Record local sources, ranges, path matching and actual remote submission, so that the results correspond to the content of this reading. The comparison process maintains original content on both sides.

Compares the full range of documents selected by the path symmetry, describing local, GitHub-specific documents with different content, as well as changes in the implementable properties that influence the use. Text differences explain the specific meaning, and binary information indicates whether or not the document is the same.

`prepare` is available to prepare for the release of changes. A separate comparison of the list of documents on both sides of the model covers a GitHub unique document. The operation is referred to below as "preparation, publication and preservation".

### Users are requested to consider alignment.

After a brief description of the overall consistency, the actual differences and their impact, the user is requested to consider retaining the respective versions, updating GitHub, adjusting to GitHub locally, or aligning the selected content only.

Following a decision by the user, a specific change is prepared in the selected direction and is carried out under the authority of the corresponding operation; the original directory follows the read-only rules of the skills, local adjustments are made to prepare internal copies and specific differences, and the actual changes to the original directory are processed through the maintenance process of the target project. The current task is to end with a statement of differences and a selection.

## Pre-establishment of warehouse: scanning, description and selection range

This section follows the order of work of ExtractStructure, “See first the actual object, then the size and use, and the final selection range,” and calculates all document types according to the need for publication. Here the steps required to fully preserve this skill are run directly under this section.

This applies to the establishment of temporary local warehouses, the preparation of copies, the production of version packages and their release to GitHub. Scan and range selection occurs before copying files, initializing Git warehouses, temporary storage and submission.

### 1. Scan user-designated objects

When the user has specified the item, directory or file, scan the object; if not, view the current directory, the description and a small amount of representative content with a light view and recommend about three physical entry points. Each entry gives a full path and a description of the purpose, pending the user's choice.

Read-only catalog scans of selected objects, counting the number, total size, main file type and main directory. Explains the actual use of the main directory, taking into account the description and the small number of readings that are available. Use to be confirmed clearly indicates “use to be confirmed”. Scan covers hidden directories and lists them separately:

- Procedures, configuration, instructions for use and development of information.
- Historical information, backup, generation results, logs, caches and temporary documents.
- This machine is configured, larger files or compressed packages, and documents that may affect GitHub 's release.
- Git metadata, symbol links, and copies of releases available within this skill.

Each major directory uses the expression “full path — actual use; number and size of files”. The exclusion requirements are listed separately; if the user provides a name for the directory that differs from the actual name, the actual correspondence is indicated. Scans are light, and the list of documents is used for the necessary reading of the range selection.

### 2. Presentation of the results of the scans and queries on the scope

The following adjustable options are provided, depending on the range of recommendations for actual content:

1. **Procedures and Usage Notes (recommended)**: A clear list of the included source code, configuration, document, and a specific directory that has been omitted.
2. **All content**: contains historical information, results, logs, caches and in-house information on scanned discoveries; clearly indicates the still-abridged Git metadata and this generated directory.
3. **Selected range **: Allow the user to specify the directory or result that needs to be carried on, and give a short example that is consistent with the actual project.

For example, complete local backup can recommend all content, and the program issues recommendations and instructions for use.

Users generally request that “the whole project” or “all but a directory” be followed by a list of candidates, followed by a question-and-answer session in conjunction with the actual discovery. Select the range after receiving the description of the current round of scans, then start copying and building the repository. Users have followed this decision when confirming the scope after the current round of scans; answers have been provided to add questions only to the scope of new or changes.

### 3. Record selection and prepare internal copies

Short recapitulation of the full source path, inclusion, omission and projected size. The range record of the task will be kept and the map and exclusions used for the copy will be implemented.

The program skips Git's own information and the run product of this skill when selecting the parent directory, preventing the copy being produced from being copied again. When the user chooses to include the published product, the specific path is clearly recorded and is included in an independent copy; this generation directory always excludes itself.

Once the scope is confirmed, an internal copy and a local warehouse are prepared below.

Release is required, with an explanation as to whether the contents of the warehouse are in the same range as the downloading attachment. GitHub's own source code downloads are taken from the entire repository that corresponds to the version label, and the uploading package attachment can contain only selected files. If the user requests to exclude information that already exists in the destination repository, indicate first that only the narrowing of the attachment will keep the documents in the warehouse and then confirm whether the warehouse distribution is adjusted. All scope adjustments are internal copies and the object remains the same.

## Find out where it's coming from.

From current tasks and information already provided by users, it has been determined that the following matters are being asked when the information that is actually necessary is not available:

- destination repository, existing or new; the new warehouse is clearly open or private.
- The file is placed in the repository root directory, or in a subdirectorial; multiple sources can be assigned a separate location.
- Updates the specified branch directly, or submits the PR.
- This time, only the content will be published, or release with a version number and a download package.

For example, `ExtractStructure/` content can be the root of a stand-alone warehouse or can be placed under `skills/extract-structure/` for an existing warehouse.

By default, publish a copy of the currently selected content. Retain the original project submission records, maintain automatic synchronization or deploy the website to different needs, and then determine the practice when the user makes it clear.

## Published language and translation

The file path, body text, code note, interface case, and GitHub release notes are available in English. The project has or is explicitly requested by the user to maintain the necessary Chinese-Chinese documents, language-to-language access and resources in the actual language version. The English project is available in English `README.md`. The bilingual project checks the use, commands and requirements of both versions using the file name and the switch in the existing two languages.

The text in other languages, as well as visible text in pictures, annexes to documents or codings, is judged by the actual publication.

The translation is in natural, accurate English. First, the sentence is understood and then expressed in the reader's familiar word and common combination. The field terminology follows the project's well-known or popular expression, retaining the necessary technical meaning, avoiding hard and straight translation, self-made terminology and far-flung complex words. The translation is followed by a review of meaning, conditions and operational steps against the original language, and then the English language is used to check whether the expression is natural. The command, code identifier, data format, and word-words are accurate. When you encounter a Chinese machine identification or program-dependent path, check the call relationship, coordinate the name change or adjust the scope of publication within this mandate.

Check by warehouse before release[Translation memorandum](references/translation-memo.md),The document is available in English, bilingual access and key translation decisions for in-skill translation preparation and review.

## Prepare internal copies and explain changes.

1. The selected file is actually copied to `results/<run-id>/source/` to preserve the content and the executable properties. Use a stand-alone file; the target item directory remains as it is.
2. On the same mission `checkout/`, prepare the destination repository and place an internal copy at the selected location. First release can be made locally by creating an empty warehouse and leaving the GitHub repository for actual release.
3. Default only adds and updates the selected path. When deleting files from the target repository, clearly lists the path to be deleted and the corresponding permission of the user.
4. The translation and review is required in the published language, the actual difference is preserved, and the user is informed of the content that will be added or modified.

The contents of the source folders that are kept as they are are `.git`, README, license, version number, packing file and running results; all the additional documents required for the release are in skills. The construction commands and other potential files are used as work directories in-house copies, and the output, temporary file and cache are assigned to the inside.

Read if you need to call the program or prepare a check[Preparation, publication and preservation](references/commands.md).The purpose and main function of the document is to describe the order, the scope of the document, the internal copy, the differences and the way the results are saved. GitHub . Scope of application: execution of directory or file copy, warehouse release, consolidation request(PR),Release package or version release(Release). This document is used for smart assistants to call in-house programs and follow user communication SKILL.md . Compare GitHub This document is also used when projects differ from local skills, prepare for comparison of copies and view differences.

## Published as confirmed

When you display a change, you follow the release authorization that the user has clearly given. Only if the objective, public scope, deletion or publication has not been authorized will you be asked about the missing decision.

Only prepared content is actually published. The internal copy, the content to be submitted or the remote branch is changed, the changes are described and reprepared; the content shown and the authorizations issued correspond to each other.

If you fail to release, record the steps to be actually completed and keep an internal copy. First look at the local results and the remote state, and then decide to continue with the resources already available, re-prepared or created. The application uses a normal roll-out, and a remote conflict is reserved for the next specific processing.

When a PR is created, if the current host provides a PR attachment tool, the real PR link is attached to the current task. This capability is used only for the delivery of the link, and the skills preparation and release process can be completed using a self-paced application.

## Delivery and preservation

Returns the real submission, PR or Release link after completion, indicating what is published in one or two sentences. Returns the full path of the internal file when only a local version of the package is produced. In case of partial failure, the completed and pending operations are reported separately.

The current working copy and correspondence of a long-term project are kept at `projects/<project-name>/` for this skill, and the preparation and record of each operation is kept at `results/<run-id>/`.

Tests, browser validations, and additional source-code changes are processed as specified by the user. Each external writing is based on the user ' s authorization to issue the specific task.
