---
name: maintain-project
description: Connect, inspect, maintain, or verify an entire research project. Use for first-time project setup, project-wide repairs, and changes that span several research components.
---

# Maintain a scientific project

## Purpose and main function

Find how an unfamiliar project works, coordinate maintenance across its components, and verify the result through its public entry points.

## Scope of application

Use for project connection, first inspection, whole-project maintenance, or work that crosses areas. For a request within one component of a managed project, go straight to its skill. Use `maintain-dataset` for data, `maintain-model` for models, `maintain-task` for tasks, `maintain-conf` for settings, `maintain-experiment` for runs, `maintain-base` for shared execution, and `maintain-optional` for standalone scripts, tests, and documentation.

## Check the project from its entry points

1. Resolve the project root and run `rh projects project status <project-root>`. Read its `AGENTS.md`, maintenance guide, runtime instructions, and public commands. Use the coordination guide to handle a missing setup or unavailable connection. Note existing work and the scope of the request.
2. Run `rh projects project check --json <project-root>` for a complete layout check or `rh projects layout check <project-root>` for a scoped structural issue. Use the project's offline launcher when its maintenance mode is offline. For installed shared skills, `rh guide skill <name>` resolves the skill file.
3. Trace an actual invocation from configuration through the selected data, model, task, and result reader. Assign each affected part to its owner. Use the [coordination guide](references/coordination.md) for connection, mode handling, responsibility routing, and cross-component evidence.
4. Verify the changes through the affected project commands. Share which components you covered, the actual paths changed, and what the checks showed. Preserve existing user work, supported commands and imports, and historical result access.

For first-time adoption, run the authorized `rh projects setup-maintenance <project-root>` before
moving or editing project files. Setup saves the initial backup. Rename an existing project root
only when the user requests a rename.

<a id="shared-project-guidelines"></a>

## Shared project guidelines

Use the [coordination guide](references/coordination.md#coordinate-structural-changes) for central layout rules, structural moves, and project-wide acceptance. The [project organization guide](references/project-organization.md) explains routing and how to verify a proposed file location.
