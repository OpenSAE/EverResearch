# ResearchHarness

ResearchHarness helps you maintain research projects and check the path from local data to saved results. It provides shared maintenance skills for coding assistants, a command-line interface for local data and Python bindings, and read-only checks for project layout and experiment records.

Each project keeps its own dependencies, data loaders, models, tasks, and run commands. ResearchHarness connects those pieces to a shared workspace and gives you a consistent way to check them.

## Quick start

Use Python 3.11 or 3.12. Keep the ResearchHarness checkout, your project, and any shared data directory under the same workspace when practical.

From the parent workspace, with a checkout at `ResearchHarness/` and an existing project at `ExampleProject/`:

```bash
python -m pip install -e ./ResearchHarness
rh projects --harness-root ./ResearchHarness register example --path ./ExampleProject
rh projects --harness-root ./ResearchHarness apply example
rh projects --harness-root ./ResearchHarness status example
```

`apply` links the shared skills into the project and adds a managed section to its assistant instructions. Start with [maintain-project](.agents/skills/maintain-project/SKILL.md) for a whole-project review.

To bind a local dataset and interpreter, then launch your project's own Python entry point:

```bash
rh projects bind example --data main=/path/to/data --python /path/to/venv/bin/python
rh projects run example -- main.py --data-root '{data:main}'
```

Replace `main.py` and `--data-root` with your project's interface. The launcher uses the selected interpreter and starts in the project's root.

## Check a project

| Command | What it checks |
| --- | --- |
| `rh projects project check ./ExampleProject` | Required directories, component source, configuration, environment documentation, and path conventions. |
| `rh projects layout check ./ExampleProject` | Naming, file placement, and directory structure. |
| `rh projects experiment check ./ExampleProject` | Saved run manifests, effective configuration, and declared output files. |
| `rh projects precheck check --help` | How to check saved evidence from a successful run and a run blocked by precheck. |

Use the project's own precheck to verify a specific data, model, and task combination. A representative run can show that the selected samples can be read, the model can be built or loaded, and the task can complete a small computation on the selected device. ResearchHarness reads the resulting evidence.

## Learn by example

- [CUB-200 classification template](src/harness/projects/template/README.md) shows how configuration, data loading, model construction, precheck, and experiment records fit together. Its offline example uses synthetic inputs. The CUB-200 recipe uses a locally supplied dataset.
- [Project layout](src/harness/projects/LAYOUT.md) and [engineering protocol](src/harness/projects/PROTOCOL.md) describe the conventions used in project reviews.
- [Workspace operations](src/harness/projects/README.md) covers shared skills, local resources, and reviewable ExtractStructure maps.

## License

[Apache License 2.0](LICENSE)
