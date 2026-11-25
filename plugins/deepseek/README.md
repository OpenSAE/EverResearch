# EverResearch for DeepSeek Harness

## Purpose and main function

Install OpenSAE's research project maintenance tools and run a first check.

## Scope of application

Use these steps for projects you can access from this environment.

## Install in DeepSeek Harness

In the following command, replace `YOUR_PROFILE` with the profile where you want
the skills, such as the one you use to run your research agent:

```sh
dsh plugin --profile YOUR_PROFILE add https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/opensae-ever-research-dsh-0.2.0.tgz
```

If the installed DSH version requires a local archive, download
[the bundle](https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer/opensae-ever-research-dsh-0.2.0.tgz), then run
`dsh plugin --profile YOUR_PROFILE add file:/absolute/path/to/opensae-ever-research-dsh-0.2.0.tgz`.
Use a DSH version compatible with the bundle's `engines.dsh` field and start
the agent with the same profile. Ask it for a research project structure check.

After the npm bundle is published, the registry install target will be
`@opensae/ever-research-dsh`. The archive works independently of registry
or marketplace listing status.

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
