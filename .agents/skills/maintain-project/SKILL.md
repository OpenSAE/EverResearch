---
name: maintain-project
description: Connect, maintain, verify, or uninstall EverResearch for a research project. Use for project setup, removal, project-wide repairs, and changes spanning multiple components.
---

# Maintain a scientific project

## Purpose and main function

Find how an unfamiliar project works, coordinate maintenance across its components, and verify the result through its public entry points.

## Scope of application

Use for project connection, first inspection, whole-project maintenance, or work that crosses areas. When the user asks to handle an identified project with EverResearch and gives no narrower task, run the default process through completion. For a new project, that request authorizes setup, routine behavior-preserving adaptations, and verification through its public entry points. A two-line invocation with `maintain-project` and a registered project name assigns the whole default local maintenance scope to the receiving agent. Proceed with the repairs in that registered checkout while preserving existing work. An explicit request to inspect, plan, or register defines a narrower scope. See [Default adoption and completion](references/coordination.md#complete-default-adoption) for the scope and decisions that require the user.

For a request within one component of a managed project, go straight to its skill. Use `maintain-dataset` for data, `maintain-model` for models, `maintain-task` for tasks, `maintain-conf` for settings, `maintain-experiment` for runs, `maintain-base` for shared execution, and `maintain-optional` for standalone scripts, tests, and documentation.

## Uninstall a project

For a request to uninstall, disconnect, or clean up a project installation, follow [Project uninstallation](references/uninstallation.md). It defines how to trace ownership, remove the connection and project-only files, preserve other users' resources, and verify the result. An explicit uninstall request selects this workflow before any setup or project-wide repair.

## Check the project from its entry points

For the two-line whole-project request, carry one registered checkout through setup,
documentation, development repairs, and real-input readiness yourself. Finish available
checks in that checkout before returning an overall report.

1. Resolve the project root from the explicit path, or from `rh projects list` for a registered name. Check the target's `AGENTS.md` and run `rh projects project status <project-root>`. Use [connection instructions](references/coordination.md#connect-an-existing-project) when setup or connection requires action. Read the project instructions for the command affected by the request.
2. Run `rh projects project check --json <project-root>` for a complete layout check or `rh projects layout check <project-root>` for a scoped structural issue. Use the project's offline launcher when its maintenance mode is offline. For installed shared skills, `rh guide skill <name>` resolves the skill file.
3. Trace the affected public command through its actual callers. Use the relevant specialist skill. Consult [source ownership](references/project-organization.md#establish-source-ownership) when the owner is unclear or the work crosses components.
4. Require the affected workflows to pass through their current public entry points and the project to pass strict layout checks. Route entry points that depend on prohibited paths to `maintain-base`. Report changed commands, verified outcomes, and remaining blockers. Preserve existing user work and historical result access.
5. Run the bounded real-input prechecks from [whole-project verification](references/coordination.md#verify-and-deliver-the-whole-project). An available model or dataset is covered when its public precheck actually passes in this checkout.

Read each linked section when its decision is needed. Keep a short record of the resulting
decision so later steps can reuse it. The generated project guide is a map to the active skills
and local resources. Use the central operations manual to look up a route when the scope or
owner is unclear.

For a named checkout, trace defects and make repairs from its own source and active shared skill
instructions. Use that checkout's own verified evidence. Treat other checkouts, unpublished release
copies, and earlier repair records as separate work unless the user selects them.

For first-time adoption, run the authorized `rh projects setup-maintenance <project-root>` before
moving or editing project files. Setup saves the initial backup. Rename an existing project root
only when the user requests a rename.

For a project still using an older maintenance directory, run setup in its existing mode to
adopt `.everresearch/`. Update the project's primary instructions and local ignore rules to use
the current entry, preserving the prior settings and project-owned files.

For every checkout that uses EverResearch, including a fresh clone carrying old instructions,
verify the public name and path in the primary and translated README, agent instructions, and
environment guide. Update active references to use EverResearch and `.everresearch/`.
Keep historical documents and explicit legacy compatibility references as provenance.

For a whole-project request, the [development path](references/coordination.md#verify-the-development-path)
is part of completion when there is an installable command or a component registry. Check it
early, while a private development environment is available. Reuse prior evidence when it
demonstrates the same behavior on the current code. For a task registry, the evidence must cover
the new task reaching its automatic precheck worker and the installed command discovering the
new task after installation. Verify that the primary contribution instructions install the tools
required by the project's quality command. Repair these gaps within the normal maintenance scope.

During first-time setup, [aim to keep each actual code run within five minutes](references/coordination.md#keep-setup-runs-short).

<a id="shared-project-guidelines"></a>

## Shared project guidelines

Use the [coordination guide](references/coordination.md#coordinate-structural-changes) for central layout rules, structural moves, and project-wide acceptance. The [project organization guide](references/project-organization.md) explains routing and how to verify a proposed file location.
