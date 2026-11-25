## Install in OpenClaw

Extract the [OpenClaw plugin ZIP](@DOWNLOAD@/ever-research-@VERSION@-openclaw-plugin.zip)
into `openclaw`, or use `plugins/openclaw` from a local
[EverResearch checkout](@REPO@).

```sh
openclaw plugins install ./openclaw
openclaw plugins list
```

Enable `ever-research` if your instance requires explicit activation, restart
the gateway and ask the agent for a check of an accessible research project.
