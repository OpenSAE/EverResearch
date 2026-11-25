## Install in Claude

**Claude Code.** Run these slash commands in a Claude Code session:

```text
/plugin marketplace add OpenSAE/EverResearch
/plugin install ever-research@ever-research
```

Reload the session and ask “Inspect this research project's directory structure.”
For an extracted copy of this folder, start Claude Code with
`claude --plugin-dir ./claude-plugin`.

**Claude web and Cowork.** Open **Customize → Plugins** and upload the
[Claude plugin ZIP](@DOWNLOAD@/ever-research-@VERSION@-claude-plugin.zip)
where custom uploads are available. In web chat, add the project files to the
conversation and enable file creation and code execution where available.
In Cowork, give the task access to the project folder. The plugin includes a
runtime copy within each skill that needs the CLI so it can also work when
Claude stages a single skill in its Python sandbox.

Claude may ask to allow the Python command. Local repository publishing also
requires Git and an authenticated GitHub CLI in the execution environment.
A Claude Code marketplace installation from GitHub and a Claude directory
listing are separate install channels.
