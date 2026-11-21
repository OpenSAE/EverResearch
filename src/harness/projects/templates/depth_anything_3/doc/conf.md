# Configuration

## Project defaults

### `conf/config.yaml`

[Default configuration](../conf/config.yaml) defines CLI inference and its
registered experiment paths. The CLI flags override these defaults. Use
`da3 auto ... --show-config` to inspect effective values. The default
checkpoint is DA3 Nested Giant Large 1.1, with CUDA, a requested resolution of
504 pixels, upper-bound resize and GLB output. The default export directory
is resolved under the checkout when available. An explicit relative
`--export-dir` resolves from the working directory.

## Model configuration

### `conf/models/model/config.yaml`

[Model presets](../conf/models/model/config.yaml) are selected by
`DepthAnything3(model_name=...)` or the checkpoint's saved model configuration.
The Giant preset uses YAML aliases to share channel dimensions between its
depth and Gaussian heads.

## Task configuration

### `conf/tasks/evaluation/config.yaml`

[Benchmark defaults](../conf/tasks/evaluation/config.yaml) accept `--config` and
dot-list overrides, with the latter taking precedence.

### `conf/tasks/streaming/config.yaml`

[Streaming presets](../conf/tasks/streaming/config.yaml) accept
`--preset base_config|tum|kitti` or a custom `--config` YAML. The built-in
presets resolve their weight files under the checkout when available.
