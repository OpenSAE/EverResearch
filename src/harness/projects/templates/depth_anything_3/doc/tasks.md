# Research tasks and prechecks

- **Depth inference** prepares views, predicts depth and camera information,
  and optionally exports the predictions. Local CLI inference checks the batch,
  calibration and resolution before loading weights. The Python inference task
  checks the loaded model's export capabilities before prediction. A named CLI
  run also processes one selected input at up to 56 pixels of requested
  resolution, exports its depth to an isolated NPZ and reads it back before
  starting the full run. Use `da3 auto INPUT --precheck-only` with the same
  local model and processing options to run only that check. The `image`,
  `images`, `colmap` and `video` commands use the same inference service.
  HTTP backend requests check batch and calibration counts and resolution
  before loading the model, then pass the requested reference view and pose
  method to the model.
- **Benchmark evaluation** computes pose or reconstruction scores from the
  selected benchmark scenes. It checks the dataset roots and modes before
  constructing readers and loading inference weights. Metrics can be read
  without the original data through the print-only entry point.
- **Streaming** processes video frames in chunks and aligns the camera poses
  and point clouds. The command checks frames, chunk overlap and local weights
  before starting the pipeline. Loop detection uses the SALAD submodule.

[Inference task](../tasks/inference/operation.py) ·
[Benchmark task](../tasks/evaluation/bench/evaluator.py) ·
[Streaming task](../tasks/streaming/pipeline.py) ·
[Precheck](../tasks/precheck/gate.py)
