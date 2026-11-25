---
name: maintain-code
description: Review, fix, or refactor research code and its callers. Trace a normal invocation through its dependencies and verify that it still delivers the requested behavior.
---

# Maintain research code

## Purpose and main function

Trace a research project's real entry points, fix confirmed problems in the responsible code, and verify the behavior its callers rely on.

## Scope of application

Use for code review, bug fixes, refactors, shared implementation, and source placement. Start from the user's request and the project's documented commands. Use `maintain-project` for whole-project coordination and `maintain-optional` for standalone scripts, tests, and documentation.

## Follow the actual call

1. Identify the entry point, intended result, actual callers, and behavior to preserve. Read the selected code, its tests, and the project instructions.
2. Trace imports, dynamic loading, subprocesses, and file access to their actual targets. Run `python -B <skill-directory>/check_dependencies.py <project-root>` for affected core code before the change and after a repair. Locate the script next to this SKILL.md.
3. Core code in `base/`, `datasets/`, `models/`, and `tasks/` can depend on other core components, the Python standard library, and installed dependencies. Keep project runtime dependencies within the core. Core components may write run outputs to `experiment/`.
4. Follow `report_before_fix`, which is on by default. Before an authorized repair, summarize the observed problem, its cause, and the proposed change. Make the smallest change that fixes the actual caller, and verify it through the project's normal entry point. Record the changed paths, observed result, and any check that could not run.

## Read details when needed

- [Code review](references/code-review.md) covers functional gaps, evidence, trade-offs, and reporting. Read it for a functional review or when judging whether a change is needed.
- [Code placement](references/code-placement.md) covers ownership, directory limits, duplicate logic, compatibility, and result paths. Read it for a move, consolidation, layout repair, or downstream compatibility check. Use `rh projects project check --json <project-root>` for layout changes.
