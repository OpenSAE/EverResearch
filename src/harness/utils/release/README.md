# Install and verify ResearchHarness

## Purpose and main function

Install the same research project maintenance rules and CLI in a terminal or an agent
workspace. Use the included BirdStudy example to verify a complete maintenance flow.

## Scope of application

Use these steps with the public artifacts and any project you are authorized to access.
The agent uses the model configured in its host. Project checks run where the project
files are accessible.

## Install

Use Python 3.11 or 3.12 and install the wheel from this release. On a machine with
[uv](https://docs.astral.sh/uv/concepts/tools/), run:

```sh
uv tool install ./researchharness-0.2.0-py3-none-any.whl
rh doctor --json
```

With a Python virtual environment already activated, the alternative is
`python -m pip install ./researchharness-0.2.0-py3-none-any.whl`. All example paths
are relative to the directory where you unpacked the release. Replace `./BirdStudy`
with your own project's path to work on a different project.

Install project-local skills and then open that project in your agent host:

```sh
rh skills install --project ./BirdStudy --agent codex --dry-run
rh skills install --project ./BirdStudy --agent codex
```

Repeat `--agent` to select more than one host. The installer supports `codex`,
`cursor`, `opencode`, `claude-code`, `github-copilot`, `gemini-cli`,
`qwen-code`, `openclaw`, `deepseek-harness`, and `generic`. The names are
installation targets. Runtime verification is documented separately. Use
`rh skills uninstall` with the same project and host flags to remove copies whose
receipt and contents still match. Local edits require review. Restart or open a new
agent session after installing. `uv tool uninstall researchharness` removes the tool.

With Node.js and uv, the npm archive can install the bundled wheel and skills
together:

```sh
npm exec --package=./opensae-researchharness-0.2.0.tgz -- researchharness --project ./BirdStudy --agent codex
```

Use `--dry-run` to print the proposed commands without installing.

### Host plugins and other environments

| Host | Installable artifact or entry |
| --- | --- |
| Codex, Cursor, GitHub Copilot, Qwen Code | Unzip the standard Agent Plugin package for host surfaces that accept portable plugins, or use project-local skills. |
| Claude Code | Unzip the Claude plugin package and load it with `claude --plugin-dir <directory>`, or use project-local skills. |
| Gemini CLI | Unzip the Gemini extension and run `gemini extensions install <directory>`, or use project-local skills. |
| OpenCode, OpenClaw, DeepSeek Harness | Install project-local skills with the matching host name. |
| Other hosts with terminal access | Install the generic project skills or unpack the Skills archive. Ask the agent to read the file returned by `rh guide skill maintain-project` and follow the applicable references. |
| Chat-only use | Share the relevant project files and agreement with your model, and run `rh projects project check` in your terminal. |

Install the CLI in the same execution environment that can access the project.
For a host with local MCP but without shell access, install the wheel with the
`mcp` extra and configure a stdio server using the following command and arguments:

```json
{
  "command": "rh",
  "args": ["mcp", "--project", "/absolute/path/to/BirdStudy"]
}
```

This server provides read-only project, layout, and experiment-record checks
plus the published project agreement. The specified path is resolved on the
machine that runs the server.

## Verify a project

Run `python verify.py .` from the unpacked release directory for a terminal
smoke test. It checks the artifact hashes and exercises installation, project
registration, the online launcher, and skill installation and removal in a
temporary environment.

1. Extract the example archive to get a disposable `BirdStudy` directory.
2. Run `rh projects project check ./BirdStudy`. The package's own documentation
   is available with `rh guide project-agreement` and `rh guide operations`.
3. Run `rh projects register bird-study --path ./BirdStudy` and
   `rh projects status bird-study`. To set up the online maintenance workflow
   in this example, enable the existing switch in
   `BirdStudy/.researchharness/mode.toml`, then run
   `rh projects setup-maintenance ./BirdStudy --online`. In that directory,
   run `python -IS .researchharness/maintain.py status`.
4. Give the agent a natural-language task and ask for a plan only. Ask for the
   current and proposed paths, the content to change, and why. Record the host
   and model names and versions. Repeat the question in a fresh session with
   another model or host to compare the plans.
5. Select a plan to apply in the disposable project, then rerun the project check
   and the project's relevant official command. For the synthetic scientific run,
   follow the BirdStudy README's **Offline Exercise**. It uses synthetic inputs
   and still requires the project's declared Python dependencies.

The installed CLI uses per-user directories for state and resources. Set
`RH_STATE_DIR` to an empty directory for an isolated acceptance test and
`RH_DATA_ROOT` to the shared directory that contains your locally bound data.
A source checkout can still be selected through `--harness-root` on project
commands, with its existing workspace and project records.

## Build the artifacts

With uv and Node.js installed, run from the ResearchHarness source directory:

```sh
rh utils release --source . --output /path/to/new-release-directory
```

Verify downloaded artifacts with `SHA256SUMS`. `CONTENTS.json` lists the
files selected for public source and wheel resources. Build inputs are selected
by the release command's allowlist.
