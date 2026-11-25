---
name: maintain-code
description: Review, fix, or refactor research code and its callers. Trace a normal invocation through its dependencies and verify that it still delivers the requested behavior.
---

# Maintain research code

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

Trace a research project's real entry points, fix confirmed problems in the responsible code, and verify the behavior its callers rely on.

## Scope of application

Use for code review, bug fixes, refactors, shared implementation, and source placement. Start from the user's request and the project's documented commands. Use `maintain-project` for whole-project coordination and `maintain-optional` for standalone scripts, tests, and documentation.

## Check project maintenance before editing

Before changing an existing project, run `rh projects project status <project-root>`.
With `managed`, use the reported guide and follow the authorized request. With `unmanaged`, follow the
repository's own rules unless the user asked to use EverResearch. For that request, use
[maintain-project](../maintain-project/SKILL.md) to plan and complete authorized setup before applying
EverResearch rules to project changes. With `unavailable`, resolve the reported connection issue
before applying those rules. Read-only inspection and planning can proceed in any state. When status
cannot be verified, keep EverResearch work to inspection and planning and explain the gap.

## Follow the actual call

1. Identify the entry point, intended result, actual callers, and behavior to preserve. Read the selected code, its tests, and the project instructions.
2. Trace imports, dynamic loading, subprocesses, and file access to their actual targets. Run `python -B <skill-directory>/check_dependencies.py <project-root>` for affected core code before the change and after a repair. Locate the script next to this SKILL.md.
3. Core code in `base/`, `datasets/`, `models/`, and `tasks/` can depend on other core components, the Python standard library, and installed dependencies. Keep project runtime dependencies within the core. Core components may write run outputs to `experiment/`.
4. Follow `report_before_fix`, which is on by default. Before an authorized repair, summarize the observed problem, its cause, and the proposed change. Make the smallest change that fixes the actual caller, and verify it through the project's normal entry point. Record the changed paths, observed result, and any check that could not run.

## Read details when needed

- [Code review](references/code-review.md) covers functional gaps, evidence, trade-offs, and reporting. Read it for a functional review or when judging whether a change is needed.
- [Code placement](references/code-placement.md) covers ownership, directory limits, duplicate logic, compatibility, and result paths. Read it for a move, consolidation, layout repair, or downstream compatibility check. Use `rh projects project check --json <project-root>` for layout changes.
