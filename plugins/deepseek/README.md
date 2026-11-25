# EverResearch for DeepSeek Harness

## Purpose and main function

Install OpenSAE's research project maintenance tools and run a first check.

## Scope of application

Use these steps for projects you can access from this environment.

## Install in DeepSeek Harness

From a terminal with Node.js, replace `YOUR_PROFILE` with your DeepSeek
Harness profile. This command supplies both the compatible DSH CLI and its
package manager.

```sh
npx --yes --package=pnpm --package=@deepseek-ai/dsh@0.2.2-rc.5 -- dsh plugin --profile YOUR_PROFILE add https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/opensae-ever-research-dsh-0.2.3.tgz
```

If you already use DSH and have `pnpm` on your PATH, run the same command
starting at `dsh plugin`. To install from a file, download
[the bundle](https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/opensae-ever-research-dsh-0.2.3.tgz) and use
`file:/absolute/path/to/opensae-ever-research-dsh-0.2.3.tgz` in place of
the URL. Review any package approval prompt before continuing.

Start your agent with the same profile and ask it for a research project
structure check. Once the npm bundle is published, the registry install
target will be `@opensae/ever-research-dsh`.

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
