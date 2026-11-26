# EverResearch for Copilot, Qwen and Skills CLI

## Purpose and main function

Install OpenSAE's research project maintenance tools and run a first check.

## Scope of application

Use these steps for projects you can access from this environment.

## Install in GitHub Copilot CLI

```sh
copilot plugin marketplace add OpenSAE/EverResearch
copilot plugin install ever-research@ever-research
```

Open Copilot in the project and ask “Inspect this research project's directory
structure.”

## Install in Qwen Code

Extract the [Agent Plugin ZIP](https://github.com/OpenSAE/EverResearch/releases/download/v0.8.1/ever-research-0.8.1-agent-plugin.zip)
into a folder called `agent-plugin`, then open Qwen Code in your project:

```sh
qwen extensions install ./agent-plugin --scope project
```

You can also use the `plugins/agent-plugin` directory inside a local
[EverResearch checkout](https://github.com/OpenSAE/EverResearch). Start a new session and ask for a project check.

## Install with the Skills CLI

From a project directory, use the repository's packaged skills. Install the
whole set so the related maintenance skills and shared runtime are available.

```sh
npx --yes skills add https://github.com/OpenSAE/EverResearch/tree/main/plugins/agent-plugin --all -y
```

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
