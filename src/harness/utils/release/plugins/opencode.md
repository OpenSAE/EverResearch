## Install in OpenCode

Extract the [OpenCode plugin ZIP](@DOWNLOAD@/ever-research-@VERSION@-opencode-plugin.zip)
into the project's `.opencode/plugins/ever-research/` directory. Keep
`package.json`, `index.mjs`, and `skills/` together. You can also copy the
`plugins/opencode` directory from an [EverResearch checkout](@REPO@).

For explicit configuration, add `"./.opencode/plugins/ever-research"` to
the `plugins` array in `opencode.json`. OpenCode V1 uses `plugin` for the
same array. Restart OpenCode and ask for a project structure check.
