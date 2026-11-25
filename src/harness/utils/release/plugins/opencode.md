## Install in OpenCode

Extract the [OpenCode plugin ZIP](@DOWNLOAD@/ever-research-@VERSION@-opencode-plugin.zip)
into the project's `.opencode/plugins/ever-research/` directory, or copy the
`plugins/opencode` directory from an [EverResearch checkout](@REPO@).

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
