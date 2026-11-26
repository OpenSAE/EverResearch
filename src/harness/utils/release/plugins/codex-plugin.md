## Install in Codex

In a local shell with Codex CLI configured, run:

```sh
codex plugin marketplace add OpenSAE/EverResearch \
  --sparse .agents/plugins --sparse plugins/codex-plugin
codex plugin add ever-research@ever-research
```

For a local copy, use `codex plugin marketplace add /path/to/EverResearch`.
In the Codex app, open Plugins and enable EverResearch from the added marketplace. Open the
project as a workspace or make it available to the environment running Codex.
Ask “Inspect this research project's directory structure.”

The [Codex plugin ZIP](@DOWNLOAD@/ever-research-@VERSION@-codex-plugin.zip)
contains the Codex plugin directory. The public OpenAI Plugins Directory and
the installable GitHub marketplace are separate channels.
