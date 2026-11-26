## Install from a terminal

Install the [EverResearch @VERSION@ wheel](@DOWNLOAD@/ever_research-@VERSION@-py3-none-any.whl) from GitHub Releases.

```sh
uv tool install @DOWNLOAD@/ever_research-@VERSION@-py3-none-any.whl
rh --version
rh doctor --json
```

If uv reports that its tool directory is missing from PATH, run
`uv tool update-shell` and open a new terminal.

In an active Python environment, pass the wheel URL to `python -m pip install`.
If [PyPI](https://pypi.org/project/ever-research/) lists this release, you can also install
with `python -m pip install ever-research==@VERSION@`. From a source checkout, use
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
