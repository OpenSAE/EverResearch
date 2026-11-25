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

The GitHub marketplace tree contains host manifests and skills. Launchers pin
one wheel by version and SHA-256 and download it from GitHub Release assets.
Platform ZIPs include a wheel for hosts that restrict downloads. The Claude ZIP
also has local runtime copies for separately staged skills. The verifier checks
skill consistency, wheel integrity, and cached use.

## Publish installer files

Store wheels, npm tarballs, ZIP files, and their checksums as attachments on a
versioned GitHub Release. Run **Publish installers** from the repository's
Actions tab on main after updating the version. It builds and verifies the
package, checks the uploaded files against the build, and publishes the Release.

Release assets are the source for download links. Use the generated marketplace
archive from that Release to update Git's text manifests, skills and runtime
checksums. Link the installer guides to the same version only after its assets
are public. Keep Release assets referenced by supported plugins available.
Previously installed 0.2.3 plugins still use the compatibility wheel at its
original URL under plugins/installer/.

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
