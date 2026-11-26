## Install in GitHub Copilot CLI

```sh
copilot plugin marketplace add OpenSAE/EverResearch
copilot plugin install ever-research@ever-research
```

Open Copilot in the project and ask “Inspect this research project's directory
structure.”

## Install in Qwen Code

Extract the [Agent Plugin ZIP](@DOWNLOAD@/ever-research-@VERSION@-agent-plugin.zip)
into a folder called `agent-plugin`, then open Qwen Code in your project:

```sh
qwen extensions install ./agent-plugin --scope project
```

You can also use the `plugins/agent-plugin` directory inside a local
[EverResearch checkout](@REPO@). Start a new session and ask for a project check.

## Install with the Skills CLI

From a project directory, use the repository's packaged skills. Install the
whole set so the related maintenance skills and shared runtime are available.

```sh
GIT_LFS_SKIP_SMUDGE=1 npx --yes skills add https://github.com/OpenSAE/EverResearch/tree/main/plugins/agent-plugin --all -y
```
