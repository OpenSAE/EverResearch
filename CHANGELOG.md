# Changelog

This file records user-facing changes to EverResearch. See [GitHub Releases](https://github.com/OpenSAE/EverResearch/releases) for published installers and checksums.

## 0.3.1

- Add `rh projects project status <path>` to report whether EverResearch maintenance is active and ready to use.
- Check the project's maintenance status before applying EverResearch rules to edits. Keep read-only inspection and onboarding plans available before setup.

## 0.3.0

- Show a read-only onboarding report for a first project check and keep showing onboarding progress while a configured project still has layout fixes. The report identifies likely model and dataset code.
- **Automation:** use `rh projects project check --strict <path>` or `--json` in scripts and CI that rely on the exit code. The default onboarding report exits 0 when the report is generated, even if the project still needs changes.
- Use the EverResearch name in the CLI and write plain-English project guidance when setting up maintenance.
- Add a lightweight example that reproduces an experiment from its recorded configuration.
- Check the published package on Linux, macOS, and Windows.

## 0.2.3

- Ship installer archives as GitHub Release downloads and verify the runtime checksum before the first use of a plugin installed from GitHub.

## 0.2.1

- Add support for Python 3.13.
