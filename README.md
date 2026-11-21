# ResearchHarness

**Less time managing research code. More time doing research.**

Research projects grow messy. Scripts pile up, configurations drift, datasets move, and experiment results become hard to trace.

ResearchHarness helps you and your coding agent keep research projects organized, maintainable, and reproducible.

## What ResearchHarness Does

- **Organize your research.** Keep datasets, models, tasks, configurations, and experiments in a consistent structure.
- **Maintain projects with AI.** Let your coding agent understand and maintain your project instead of fixing files one by one.
- **Make experiments traceable.** Keep configurations, execution records, and results connected.
- **Catch problems early.** Check project structure and experiment records before small inconsistencies become bigger problems.
- **Reuse what works.** Apply the same research maintenance workflows across different projects.

## How It Works

**Start from scratch or bring your existing code.**

Whether you're building a new research project or cleaning up an existing codebase, ResearchHarness helps your coding agent organize it into a consistent structure.

```text
YourProject/
├── base/          # Shared code and execution
├── datasets/      # Data loading and processing
├── models/        # Model implementations
├── tasks/         # Training, evaluation, and analysis
├── conf/          # Experiment configurations
├── experiment/    # Experiment records and results
├── scripts/       # Standalone utilities
├── tests/         # Tests and checks
└── doc/           # Project documentation
```

Each component has a clear responsibility, making it easier for agents to understand, modify, and extend your research without losing track of how everything fits together.

**ResearchHarness keeps code and results reusable, readable, and traceable throughout agent-driven development.**

As your project evolves, shared maintenance workflows help keep its structure, configurations, and experiment records consistent.

## See It in Action

**From scattered research code to an organized, maintainable project.**

**Before ResearchHarness**

- Scripts and configurations scattered across folders
- Dataset paths tied to individual machines
- Experiments difficult to track or revisit
- Every new project requires another round of cleanup

**With ResearchHarness**

- Consistent project organization
- Reusable workflows for your coding agent
- Local data and environments connected to each project
- Structured experiment records and checks

*A real project walkthrough will show the workflow from project inspection to organized code and reviewable results.*

## Get Started

Connect an existing research project in a few commands.

```bash
pip install -e ./ResearchHarness
rh projects --harness-root ./ResearchHarness register myproject --path ./MyProject
rh projects --harness-root ./ResearchHarness apply myproject
```

Then ask your coding agent:

> Review and maintain this research project using ResearchHarness.

### One Skill to Coordinate Your Research

**`maintain-project` is the central coordinator of ResearchHarness.**

It guides your coding agent through the entire project, coordinating specialized skills for each component:

| Skill | What it manages |
| --- | --- |
| [`maintain-dataset`](.agents/skills/maintain-dataset/SKILL.md) | Datasets, preprocessing, and data loading |
| [`maintain-model`](.agents/skills/maintain-model/SKILL.md) | Model implementations and variants |
| [`maintain-task`](.agents/skills/maintain-task/SKILL.md) | Training, evaluation, and research tasks |
| [`maintain-conf`](.agents/skills/maintain-conf/SKILL.md) | Configurations and parameters |
| [`maintain-experiment`](.agents/skills/maintain-experiment/SKILL.md) | Experiment execution and result records |
| [`maintain-base`](.agents/skills/maintain-base/SKILL.md) | Shared code and execution workflows |

You don't need to manage every component separately. Start with [`maintain-project`](.agents/skills/maintain-project/SKILL.md) for project-wide work, or use a specialized skill when you want to focus on one part.

As your research evolves, the same workflows help keep your code organized and your results traceable.

## Built for Everyday Research

Whether you're starting a new experiment, adding a dataset, switching models, or returning to an old project, ResearchHarness gives you a consistent way to keep your research code under control.

**Your research keeps moving. Your codebase should keep up.**

## Future Development

- **Long-Horizon Research** — Set ambitious research goals and let AI agents autonomously plan, execute, and refine research workflows.
- **Knowledge Interface** — Help AI agents understand scientific concepts, reason with domain knowledge, and actively contribute to research discussions and paper writing.
- **Research RSI** — Enable AI agents to progressively improve their research capabilities through domain knowledge, experimental feedback, and human supervision.

## License

[Apache 2.0](LICENSE)
