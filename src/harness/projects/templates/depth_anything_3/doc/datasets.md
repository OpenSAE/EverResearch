# Dataset and media selection

| Input | Reader | Normal workflow |
| --- | --- | --- |
| SOH example image pair | [Media handlers](../datasets/media/input_handlers.py) | `da3 auto assets/examples/SOH` finds and sorts the two images. |
| Images, video and COLMAP | [Media handlers](../datasets/media/input_handlers.py) | Image inputs use path order, video uses sampled frame order, and COLMAP pairs image paths and camera metadata. |
| Streaming image sequence | [Frame reader](../datasets/media/streaming_frames.py) | The streaming task uses sorted JPG and PNG frames. |
| ETH3D, 7Scenes, ScanNet++, HiRoom, DTU, DTU-64 | [Benchmark readers](../datasets/benchmark/datasets) | The evaluator selects the datasets listed in its effective configuration. [Dataset preparation and metrics](code/guides/benchmark.md) |

The bundled images and video remain available under `assets/examples/`.
The underlying data files reside under `data/media/examples/`.
