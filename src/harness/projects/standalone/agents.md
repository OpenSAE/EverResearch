## Maintain this checkout

Use the project instructions above for ordinary work and read-only inspection. EverResearch is an optional maintenance tool.

- **First use.** If `.researchharness/mode.toml` is missing and the user has authorized EverResearch setup, run `rh projects setup-maintenance . --online` for online maintenance or `rh projects setup-maintenance .` for a standalone checkout. An older `mode.json` requires a current mode selection as well.
- **Offline maintenance.** With `enabled = false`, use the [offline guide](.researchharness/offline/operations.md).
- **Online maintenance.** With `enabled = true`, run `python -IS .researchharness/maintain.py status` and follow the relevant section of the reported guide. If the connection fails, report the error and pause work that needs the central guide.

For an authorized structure check, run `python -IS .researchharness/maintain.py check` from the project root. Use the project's own entry points to install, run tasks, and read their results.
