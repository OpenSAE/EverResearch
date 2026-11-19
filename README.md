# ResearchHarness

## Purpose

ResearchHarness shares maintenance workflows across research projects, connects each project to local data and Python, and records reviewable ExtractStructure maps. It also provides independent utilities for environment inspection, transfers, and archive extraction.

## Scope

Research projects can keep their own source layout, configuration, run commands, and GitHub review workflows. Use ResearchHarness to attach the local resources and shared skills a project needs.

## Install and connect a project

Install from this checkout with `python -m pip install -e .`. The equivalent source command is `PYTHONPATH=src python -m harness.cli`. Keep `ResearchHarness/`, a shared `data/` directory, and your research repositories as siblings in a workspace.

From the parent workspace, with a project repository at `example/`, run:

```bash
rh projects --harness-root ./ResearchHarness init-workspace
rh projects register example --path ./example
rh projects status example
rh projects apply example
```

`init-workspace` initializes the parent of the ResearchHarness checkout. Once initialized, commands can find the workspace by walking up from the current directory. Use `--harness-root` to select the checkout explicitly. `apply` synchronizes shared skills and the managed section of the project's instructions. The project owns its local skills and other instructions.

## Bind local data and Python

```bash
rh projects bind example --data main=/path/to/data --python /path/to/venv/bin/python
rh projects list
rh projects resources example
rh projects run example -- main.py --data-root '{data:main}'
rh projects run --env 'PROJECT_DATA_ROOT={data:main}' example -- main.py
```

Replace the example Python arguments and environment variable with the project's actual interface. Each data directory has a name. Relative binding inputs are interpreted from the project root. The selected Python runs from that root, and the project handles its own configuration, preflight checks, environment records, and results. Use `--remove-data NAME` or `--clear-python` to clear a binding.

## Store and review structure maps

Export a trusted standalone HTML map from ExtractStructure, then run:

```bash
rh projects structure add example /path/to/index.html --revision COMMIT_OR_SNAPSHOT --scope src
rh projects structure list example
rh projects structure show example ARTIFACT_ID
rh projects structure review example ARTIFACT_ID --decision approved --note 'Reviewed the structure for this scope'
```

Open the local path in the `page` field. Reviews may also record `changes-requested`. The source revision, scope, and content digest identify the exact page under review. Project code, plans, and merges follow the project's GitHub workflow.

## Run standalone utilities

```bash
rh utils archive --help
rh utils transfer --help
rh utils probe --output /path/to/environment.json
rh utils compare /path/to/before.json /path/to/after.json
```

See the [transfer and archive guide](src/harness/utils/transfer/README.md) for command arguments, filtering, receipts, and recovery procedures.

## Project layout and maintenance

- [Shared skills and local workspace operations](src/harness/projects/README.md) covers setup, project organization, and ongoing maintenance.
- [build-project](.agents/skills/build-project/SKILL.md) guides the initial organization of an unfamiliar research project. The shared maintenance skills cover the base runtime, datasets, models, tasks, experiments, and optional assets.
- [The CUB classification template](src/harness/projects/template/README.md) demonstrates a runnable research workflow with preflight checks, model and dataset components, and experiment records.
- [Development instructions](src/agent/AGENT_FLOW.md) and [command tests](tests/) support maintenance of ResearchHarness itself.
