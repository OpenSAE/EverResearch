# Project shared skills and in-house operations

## Purpose

Lists the skills portals for project collation and maintenance, sharing skills in a synchronized manner with scientific projects, maintaining in-house data and Python selections, and preserving reversible structural results.

## Scope

You can start with the actual entry point and register as needed.

## Overall and dedicated maintenance of the project

**[`maintain-project`](../../../.agents/skills/maintain-project/SKILL.md) is the main entry point for the overall maintenance of scientific projects. ** applies to access to strange projects, to combo directories, to check the existing project as a whole and to process cross-component changes. It defaults on access to the applicable know-how, and then consolidates the changes and acceptance evidence from the actual entry point and product inspection level.

The following specific skills are used directly when handling a single job. `maintain-project` Entry of specific skills to be applied on a case-by-case basis.

| Skills | Application of work and duties |
| --- | --- |
| [`maintain-base`](../../../.agents/skills/maintain-base/SKILL.md) | Connect commands, configurations, data, models and missions, maintain distribution, share operational resources and read and write results. |
| [`maintain-dataset`](../../../.agents/skills/maintain-dataset/SKILL.md) | Add and remove data sets and presets, and maintain sample preparation, division, registration and task reading. |
| [`maintain-model`](../../../.agents/skills/maintain-model/SKILL.md) | Adds and removes models or variants to maintain the construction, weight load and task compatibility. |
| [`maintain-task`](../../../.agents/skills/maintain-task/SKILL.md) | Adding or removing research tasks, models or results interfaces, and maintaining the interface of calculations, indicators and results. |
| [`maintain-conf`](../../../.agents/skills/maintain-conf/SKILL.md) | Add, remove or modify public parameters to check meanings, default values, coverage and historical compatibility with actual consumers. |
| [`maintain-experiment`](../../../.agents/skills/maintain-experiment/SKILL.md) | The report is maintained using the experimental formulation and the single parameter to perform, track, restore, read or screen experiments. |
| [`maintain-optional`](../../../.agents/skills/maintain-optional/SKILL.md) | Maintenance of independent scripts, tests, component documents and external documents kept with the project. |
| [`maintain-tmp`](../../../.agents/skills/maintain-tmp/SKILL.md) | The catalogue, use and closure of the one-time project work is managed and applies to short-term scripts and documents that cannot be carried out at the existing entrance or official location. |
| [`maintain-code`](../../../.agents/skills/maintain-code/SKILL.md) | Review and maintenance of designated codes and their upstream and downstreams, and cleaning of temporary documents once the core results are reproduced through the public entry point. |
| [`maintain-skill`](../../../.agents/skills/maintain-skill/SKILL.md) | The specified skills are assessed in real-use scenarios, the results of which are biased and are repaired and repeated. |
| [`maintain-knowledge`](../../../.agents/skills/maintain-knowledge/SKILL.md) | The organization and preservation of knowledge worthy of long-term use applies to the recording of ideas, reading of existing knowledge and additional comments. |

## Project access

The project README first describes how to install dependent, configured data and the environment independently and run from the project’s public entry point. Access to ResearchHarness allows you to share skills, bind the machine resources and register the results of the structure.

[Project access and in-house resources](../core/PROJECT.md)Provisions ResearchHarness,The following commands are executed from the parent's work area, with examples of which the project warehouse is located: `example/`.

```bash
rh projects --harness-root ./ResearchHarness register example --path ./example
rh projects --harness-root ./ResearchHarness status example
rh projects --harness-root ./ResearchHarness apply example
rh projects --harness-root ./ResearchHarness set example --skills off
```

`manage.py` Read Centre `.agents/skills/` Here we go. `SKILL.md` If the project is used. `.agents/skills/` As an alias for your own directory, the central skills are placed in `.agents/researchharness-skills/`.The central identity, shared set-up and engineering experience of existing projects are located at the central location of the project. `src/project/<Item>/`.Project own code review, plan and collaborate to authorize project use GitHub Process.

## Project scope description

- [Catalogue of research projects and documentation functions](LAYOUT.md)Description of layout, document attribution and call relationship for access, organization and extension of projects using the layout.
- [Project engineering agreement](PROTOCOL.md)Description of project inspection, precheck, performance, environment, results and manual judgement applicable to projects subject to common engineering agreement.
- [Scientific project documentation and maintenance reporting](DOCUMENTATION.md)Provide for directory, fixed entries, environmental and experimental records and the use of evidence for the creation of project documentation, maintenance or review functions.
- [CUB-200 Classification reference items](template/README.md)Accompanying demonstration components, prechecks and results, applicable to the comparison of runable project samples.

## Inner data, Python and structural results

`rh projects bind`, `resources` and `run` manage their own path and use the selected Python to call the original entry to the project. Use `{data:name}` to send the registered data catalogue to the project's parameter or environmental variable. `rh projects install` Use the same Python installation statement to rely on.

The binding record is kept at `src/project/<project>/resources.json` for ResearchHarness. Structure results and review records are kept at `structure/` under the same item directory.

`rh projects structure add` Receives a credible independent HTML exported by ExtractStructure, as well as source versions and analytical ranges. Use `list` or `show` to find a page and use `review` to record the decision on that version. View the page directly to open the path to the machine to which the command returns.

[Use Example](../../../README.md)Description of the specific calls for installation and commands, applicable to new project access and to the home-based operation of existing projects.
