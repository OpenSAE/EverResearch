---
name: maintain-task
description: Add, change, or remove a research task such as training or evaluation. Use for task registration, prechecks, dataset and model compatibility, execution, and result interfaces.
---

# Maintain research tasks

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

## Purpose and main function

Keep the project's scientific tasks runnable through their public entry points. Organize named tasks and their shared precheck under `tasks/`.

## Scope of application

Use this skill to add a task, change its algorithm, parameters, checks, metrics, or outputs, or remove a mode or output. Start with the project's `AGENTS.md`, README, or operating guide. Identify the selected data and model, the task's computation, and the readers that depend on its results. Check those readers when changing or removing an output.

The [task procedures](references/procedures.md) explain task structure and the workflow for each kind of change.

## Check project maintenance before editing

Before applying EverResearch rules to project edits, check the project's maintenance status with
`rh projects project status <project-root>`. If no mode has been selected, follow the repository's own rules. When the user
asks to use EverResearch on that project, hand off to [maintain-project](../maintain-project/SKILL.md)
for authorized setup before applying these rules. Read-only inspection and planning can proceed
before setup.

With `managed`, use
the reported guide and follow the authorized request. If the connection is unavailable or its
status cannot be verified, explain the gap and resolve it before applying EverResearch rules.


## Automatic precheck before running a formal task

Provide a precheck under `tasks/precheck/` for every public scientific task. Call it automatically
from the normal task command and expose a mode that ends after the bounded precheck. Follow
[the task precheck procedure](references/procedures.md#run-a-bounded-precheck-for-every-task) to
exercise the selected data, model, computation, and result contracts and verify the rejection path.

## Document Sync & Delivery

Synchronizes the task entries and the configuration, components and results that are affected. Report on the available combination, the actual output of the task, how the indicator is explained and how the existing reader or historical result is affected. `maintain-conf` Collaboration.

The changes are recorded in the project-by-project project file.

## Item-by-line

The sub-missions can be independently called. The attribution checks which input it relies on, which operational product it uses, what it delivers, and by whom it continues to read. There are multiple tasks for which the operation is provided in a single module. The existing commands can continue to point to the same achievement.

The research logic for the sub-task of the same task is placed in the name module of the task. When cross-task reading of the sampler and label, tectonic model, restoration of the training status or serialization file, the data, model, and the performance of the operating layer are reused separately. When a directory is found to be clustered only by the reuse relationship, the object, the actual caller, and the rules it maintains are identified and placed in the position of the responsible object.

For projects using a layered configuration, each sub-task has its own parameter prefix, reflecting the task and sub-task name. Only the value that changes the result or execution mode in the sub-task enters the prefix. The choice of multiple sub-tasks is provided by task integration, and the document lists the reuse relationship and the conditions of validity.

The task entry explains the purpose, common constraints and the overall result. The sub-task entry explains the distinction, the mode of call, the input output and the upstream/downstream relationship. Synchronizes the distribution, configuration, caller and document when the ability is added, merged, subtracted or modified.

The main text of the task page follows the actual work to clear tasks and steps, products and next steps. When you refer to a workstream description or other document, you summarize its scope and the specific operations that the reader can find.
