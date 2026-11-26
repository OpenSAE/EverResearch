# EverResearch for OpenCode

## Purpose and main function

Install OpenSAE's research project maintenance tools and run a first check.

## Scope of application

Use these steps for projects you can access from this environment.

## Install in OpenCode

Extract the [OpenCode plugin ZIP](https://github.com/OpenSAE/EverResearch/releases/download/v0.3.1/ever-research-0.3.1-opencode-plugin.zip)
into the project's `.opencode/plugins/ever-research/` directory, or copy the
`plugins/opencode` directory from an [EverResearch checkout](https://github.com/OpenSAE/EverResearch).

Add the skill directory to your project’s `opencode.json`. Merge the path
into your existing settings if the file is already present:

```json
{
  "skills": {
    "paths": ["./.opencode/plugins/ever-research/skills"]
  }
}
```

This skill configuration works in OpenCode V1 and V2. Run
`opencode debug skill` to check that `maintain-project` appears. Open your
project in OpenCode and ask for a project structure check.

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

## Runtime compatibility

The repository skills are synchronized with EverResearch source. This distribution's launcher uses the published EverResearch 0.3.1 wheel. For source workflows that require the `.everresearch/` setup or a source-only command, use the CLI from the corresponding [EverResearch source checkout](https://github.com/OpenSAE/EverResearch/commit/9b036cb2109788a8545724a03c313502d255d187). Use the project's existing maintenance entry point when working with the published runtime.
