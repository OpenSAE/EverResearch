# EverResearch for the terminal

## Purpose and main function

Install OpenSAE's research project maintenance tools and run a first check.

## Scope of application

Use these steps for projects you can access from this environment.

## Install from a terminal

Install the OpenSAE CLI from [PyPI](https://pypi.org/project/ever-research/).

```sh
uv tool install ever-research
rh doctor --json
```

If uv reports that its tool directory is missing from PATH, run
`uv tool update-shell` and open a new terminal.

EverResearch 0.2.1 adds Python 3.13 support. You can also install the
[same wheel from GitHub](https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/ever_research-0.2.3-py3-none-any.whl).

```sh
uv tool install --python 3.13 https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/ever_research-0.2.3-py3-none-any.whl
```

In an active Python environment, install with `python -m pip install ever-research`
or use the GitHub wheel URL. From a source checkout, use
`python -m pip install .` for a regular installation or add `-e` for development.
Use `uv tool uninstall ever-research` to remove the uv installation.

From a project directory, install the CLI and skills together from the npm archive:

```sh
npm exec --yes --package=https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/opensae-ever-research-0.2.3.tgz -- ever-research
```

Node.js 18 or newer is required for this installer. It defaults to the current
project and detects installed agent commands. You can select agents explicitly
with `--agent codex --agent claude-code`, choose a project with
`--project ./MyProject`, and use `--dry-run` to preview the commands.
For a terminal installation through the wheel, run
`rh skills install --project . --agent codex` to add project-local skills.

## Use EverResearch

Share the project folder with your agent, then ask “Inspect this research
project’s layout and tell me what you verified.” Local terminal hosts use
Python 3.11, 3.12, or 3.13. The agent starts `rh` from the skill. GitHub
marketplace installs download EverResearch's pinned wheel from OpenSAE's
repository and verify its checksum. Downloadable plugin ZIPs carry the wheel.
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
