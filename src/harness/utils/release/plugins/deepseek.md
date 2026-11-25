## Install in DeepSeek Harness

From a terminal with Node.js, replace `YOUR_PROFILE` with your DeepSeek
Harness profile. This command supplies both the compatible DSH CLI and its
package manager.

```sh
npx --yes --package=pnpm --package=@deepseek-ai/dsh@0.2.2-rc.5 -- dsh plugin --profile YOUR_PROFILE add @DOWNLOAD@/opensae-ever-research-dsh-@VERSION@.tgz
```

If you already use DSH and have `pnpm` on your PATH, run the same command
starting at `dsh plugin`. To install from a file, download
[the bundle](@DOWNLOAD@/opensae-ever-research-dsh-@VERSION@.tgz) and use
`file:/absolute/path/to/opensae-ever-research-dsh-@VERSION@.tgz` in place of
the URL. Review any package approval prompt before continuing.

Start your agent with the same profile and ask it for a research project
structure check. Once the npm bundle is published, the registry install
target will be `@opensae/ever-research-dsh`.
