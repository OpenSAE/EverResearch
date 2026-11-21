# Public interfaces and runtime

`main.py` launches image prediction, VOS, training, the evaluator and the video benchmark from a source checkout. The installed distribution retains the `sam2` and `training` modules. The shared mapping in [imports.py](../base/segment_anything/imports.py) connects those names to the responsible source directories. Older Hydra targets and public predictor imports use the same implementation files.

The configuration loader registers the published recipe names from [`conf/`](conf.md). Source-root defaults resolve from the checkout. Explicit relative command-line paths resolve from the current directory. A wheel user outside a source checkout supplies `--experiment-root` for image predictions that write results.
