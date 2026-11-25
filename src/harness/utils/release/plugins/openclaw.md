## Install in OpenClaw

Extract the [OpenClaw plugin ZIP](@DOWNLOAD@/ever-research-@VERSION@-openclaw-plugin.zip)
into `openclaw`, or use `plugins/openclaw` from a local
[EverResearch checkout](@REPO@).

```sh
openclaw plugins install ./openclaw --accept-capabilities
openclaw plugins list
```

Confirm the local source when prompted. Enable `ever-research` if your instance requires explicit activation, restart
the gateway and ask the agent for a check of an accessible research project.
