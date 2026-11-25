# EverResearch for Codex

## Purpose and main function

Install OpenSAE's research project maintenance tools and run a first check.

## Scope of application

Use these steps for projects you can access from this environment.

## Install in Codex

In a local shell with Codex CLI configured, run:

```sh
codex plugin marketplace add OpenSAE/EverResearch
codex plugin add ever-research@ever-research
```

For a local copy, clone the [EverResearch repository](https://github.com/OpenSAE/EverResearch), then substitute
its checkout path for `OpenSAE/EverResearch` in the first command. In the Codex
app, open Plugins and enable EverResearch from the added marketplace. Open the
project as a workspace or make it available to the environment running Codex.
Ask “Inspect this research project's directory structure.”

The [Codex plugin ZIP](https://github.com/OpenSAE/EverResearch/releases/download/v0.2.3/ever-research-0.2.3-codex-plugin.zip)
contains the Codex plugin directory. The public OpenAI Plugins Directory and
the installable GitHub marketplace are separate channels.

## Use EverResearch

Share the project folder with your agent, then ask “Inspect this research
project’s layout and tell me what you verified.” Local terminal hosts use
Python 3.11, 3.12, or 3.13. The agent starts `rh` from the skill. GitHub
marketplace installs download EverResearch's pinned wheel from the matching GitHub Release and verify its checksum. Downloadable plugin ZIPs carry the wheel.
The launcher caches the runtime and may fetch Python dependencies from the
configured package index. You can use the supported interpreter already available to the host.

In an environment with file access only, the agent can review the available
files and produce a plan. It reports any automated checks the environment
could not run. Use a terminal-enabled host for complete checks.

## File access and network use

Project inspection reads the selected files and runs local checks. The CLI
writes its own local cache and state. Project registration, maintenance, and
experiment execution read or change the project as requested. Running a
project's own entry point follows that project's commands and dependencies.

GitHub publishing is a separate skill. When requested, it prepares a local
copy and calls Git and GitHub CLI for the selected repository. GitHub CLI
handles authentication using its own login or configuration, and sends approved
files and Git metadata to GitHub. The Python publisher does not extract the
login token. The Hugging Face skill separately uses Hugging Face credentials and
contacts Hugging Face for requested downloads, uploads, or Space operations.

For the project layout, install options, and issue tracking, open the
[EverResearch repository](https://github.com/OpenSAE/EverResearch).
