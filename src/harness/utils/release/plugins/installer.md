## Install from a terminal

Install the OpenSAE CLI from [PyPI](https://pypi.org/project/ever-research/).

```sh
uv tool install ever-research
rh doctor --json
```

If uv reports that its tool directory is missing from PATH, run
`uv tool update-shell` and open a new terminal.

EverResearch 0.2.1 adds Python 3.13 support. You can also install the
[same wheel from GitHub](@DOWNLOAD@/ever_research-@VERSION@-py3-none-any.whl).

```sh
uv tool install --python 3.13 @DOWNLOAD@/ever_research-@VERSION@-py3-none-any.whl
```

In an active Python environment, install with `python -m pip install ever-research`
or use the GitHub wheel URL. From a source checkout, use
`python -m pip install .` for a regular installation or add `-e` for development.
Use `uv tool uninstall ever-research` to remove the uv installation.

From a project directory, install the CLI and skills together from the npm archive:

```sh
npm exec --yes --package=@DOWNLOAD@/opensae-ever-research-@VERSION@.tgz -- ever-research
```

Node.js 18 or newer is required for this installer. It defaults to the current
project and detects installed agent commands. You can select agents explicitly
with `--agent codex --agent claude-code`, choose a project with
`--project ./MyProject`, and use `--dry-run` to preview the commands.
For a terminal installation through the wheel, run
`rh skills install --project . --agent codex` to add project-local skills.
