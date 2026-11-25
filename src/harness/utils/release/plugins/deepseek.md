## Install in DeepSeek Harness

In the following command, replace `YOUR_PROFILE` with the profile where you want
the skills, such as the one you use to run your research agent:

```sh
dsh plugin --profile YOUR_PROFILE add @DOWNLOAD@/opensae-ever-research-dsh-@VERSION@.tgz
```

If the installed DSH version requires a local archive, download
[the bundle](@DOWNLOAD@/opensae-ever-research-dsh-@VERSION@.tgz), then run
`dsh plugin --profile YOUR_PROFILE add file:/absolute/path/to/opensae-ever-research-dsh-@VERSION@.tgz`.
Use a DSH version compatible with the bundle's `engines.dsh` field and start
the agent with the same profile. Ask it for a research project structure check.

After the npm bundle is published, the registry install target will be
`@opensae/ever-research-dsh`. The archive works independently of registry
or marketplace listing status.
