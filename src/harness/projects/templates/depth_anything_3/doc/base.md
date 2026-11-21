# Runtime and interfaces

[The command module](../base/depth_anything/commands.py) selects image,
video or COLMAP input, resolves the configuration and dispatches the
inference service. It also reads saved executions through `da3 results`.
[The Python interface](../base/depth_anything/interface.py) exposes the model
and delegates inference to the task implemented in `tasks/inference/`.
Use [the command guide](code/guides/commands.md) for CLI options
and [the interface guide](code/guides/interface.md) for Python call signatures.
