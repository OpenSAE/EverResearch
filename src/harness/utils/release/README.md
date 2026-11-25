# Build and verify EverResearch

## Purpose and main function

Produce and verify the OpenSAE CLI, npm installer, and agent plugins from the same source.

## Scope of application

Use these steps for a source checkout or an unpacked set of build artifacts.
For installation, use the [EverResearch README](https://github.com/OpenSAE/EverResearch#install)
or the README in your platform's plugin folder.

## Build

With uv and Node.js installed, run from an active source checkout:

```sh
uv run rh utils release --source . --output ./build-ever-research
python build-ever-research/verify.py build-ever-research
```

The build produces the `ever-research` Python wheel, `@opensae/ever-research` npm
installer, DeepSeek npm bundle, separate host ZIPs, a GitHub marketplace archive,
the BirdStudy example, checksums and an inventory. Each host receives its own
installation guide. Verify the pack's files against `SHA256SUMS`.

The GitHub marketplace tree contains the host manifests and skill files. Runtime
launchers share one wheel from `plugins/installer/`, pinned by filename and
SHA-256. Platform ZIPs include a local wheel for environments that restrict
GitHub downloads. The Claude ZIP also includes local runtime copies for skills
that may run in separate sandboxes. The verifier checks skill consistency across
hosts, confirms that the marketplace tree has no embedded wheels, and tests
download integrity and reuse of the local cache.
Keep published wheels at their versioned installer URLs as long as a supported
marketplace plugin refers to them. Each release adds at most one shared wheel.
Numbered plugin ZIPs and the npm installer can also carry local runtime copies.

## Verify a project

Extract the example ZIP. Ask an agent to check the BirdStudy directory, or run
`rh projects project check ./BirdStudy` with the CLI. Check reports should name
the project files and checks they actually verified. To test a disconnected
environment, make project files accessible to the agent and verify it can
report a static review with the unavailable checks identified.

## Optional local MCP server

Install the OpenSAE wheel with the `mcp` extra for a local stdio MCP server.
Configure the host with the following command and arguments. Use a project path
that exists on the server machine.

```json
{
  "command": "rh",
  "args": ["mcp", "--project", "/absolute/path/to/BirdStudy"]
}
```

The server exposes read-only project, layout and experiment-record checks.
