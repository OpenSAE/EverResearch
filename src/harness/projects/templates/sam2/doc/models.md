# SAM 2 models

## Purpose and features

Match supported model variants to the Hydra recipe, checkpoint and prediction interface.

## Scope

Use this page for local image or video prediction and to identify the starting architecture for fine-tuning.

Both published generations have Hiera Tiny, Small, Base Plus and Large variants. The image command takes identifiers such as `sam2.1-hiera-large` and `sam2-hiera-tiny`. The identifier selects the architecture and the checkpoint filename. Use `--checkpoint` for another local copy of the matching weights. The Python builders accept the Hydra recipe and checkpoint path explicitly. [Released checkpoint and recipe tables](../README.md#model-description)

Image prediction and the video predictor share the model implementation in `sam2/modeling/`. Image prompting produces masks, predicted mask quality scores and lower-resolution logits. Video prediction uses a predictor with memory and an inference state to propagate masks across frames. The video builder also supports an optimized predictor configured for compilation. [Image and video interfaces](../README.md#getting-started)

The MOSE recipe fine-tunes SAM 2.1 Hiera Base Plus using the training model wrapper. The benchmark CLI also starts with Base Plus by default, while the image command starts with Large to match the README example. [MOSE fine-tuning recipe](../conf/tasks/fine_tuning/config.yaml) · [VOS command](code/video.md)
