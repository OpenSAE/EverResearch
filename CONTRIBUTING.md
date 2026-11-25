# Contributing to EverResearch

This guide covers reporting issues and changing the CLI, shared skills, or reference projects.

- For an installation issue, include your platform, Python version, and the output of `rh doctor --json`.
- For a project onboarding issue, include the command you ran, the relevant part of its report, and what you expected. A small example directory tree makes it easier to reproduce.
- For a change to a skill or project rule, show a workflow that needs it. Include the relevant verification result in your pull request.

Install the CLI from your checkout with `python -m pip install -e .`. Run `python -m pytest` with pytest installed and try `rh utils quick-demo ./QuickDemo` in a fresh directory for first-run changes.

See the [project workflow guide](src/harness/projects/README.md) and the [distribution guide](src/harness/utils/release/README.md) for the corresponding maintenance commands.
