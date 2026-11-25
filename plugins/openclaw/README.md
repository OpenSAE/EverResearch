# EverResearch for OpenClaw

## Purpose and main function

Install OpenSAE's research project maintenance tools and run a first check.

## Scope of application

Use these steps for projects you can access from this environment.

## Install in OpenClaw

Extract the [OpenClaw plugin ZIP](https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/ever-research-0.2.0-openclaw-plugin.zip)
into `openclaw`, or use `plugins/openclaw` from a local
[EverResearch checkout](https://github.com/OpenSAE/EverResearch).

```sh
openclaw plugins install ./openclaw
openclaw plugins list
```

Enable `ever-research` if your instance requires explicit activation, restart
the gateway and ask the agent for a check of an accessible research project.

## Use EverResearch

Share the project folder with your agent, then ask “Inspect this research
project’s layout and tell me what you verified.” Local terminal hosts use
Python 3.11 or 3.12. The plugin supplies the `rh` program and the agent starts
it from the skill on first use. It prepares an isolated environment in the
user cache and may download Python dependencies from the configured package
index. You can use the supported interpreter already available to the host.

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
