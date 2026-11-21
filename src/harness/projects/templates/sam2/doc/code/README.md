# Source map

| Workflow | Implementation |
| --- | --- |
| Point-prompt prediction and readback | [Image task](../../tasks/image_segmentation/image_inference.py), [RGB reader](../../datasets/notebook_images/source.py), [model construction](../../models/segment_anything/build.py) |
| VOS inference | [Batch inference](../../tasks/video_segmentation/inference.py), [tracking predictor](../../tasks/video_segmentation/predictor.py) |
| Fine-tuning | [Launcher](../../base/training/train.py), [trainer](../../tasks/fine_tuning/trainer.py), [VOS dataset](../../datasets/video_objects/vos_dataset.py), [training model](../../models/segment_anything/training/model.py) |
| SA-V / DAVIS scoring | [Evaluation command](../../tasks/evaluation/evaluator.py), [metrics](../../tasks/evaluation/benchmark.py) |

## Local checks

Run `python -m pytest -q` from the source root with the configured Python environment. The suite exercises recipe selection, sparse VOS input handling, launcher overrides and image prediction serialization with isolated inputs.

Run `python main.py image --print-config --dataset notebook_images` to inspect the source checkout defaults from any working directory.
