# Models and checkpoints

## Use and entry point

The PyTorch task uses `--model-path` to select a checkpoint and `--device` to select execution placement. Its loader reuses the LLaVA tokenizer, model and vision-tower builder. [Model adapter](../models/fast_vision/__init__.py) [Builder](../models/model/builder.py)

## Shared parameters

The default recipe selects the published 0.5B Stage 3 folder in project-local `data/checkpoints/`. An explicit local checkpoint can live in any directory. The release list specifies model size, training stage and source URL. [Published weights](../README.md#model-zoo) [Device and checkpoint options](conf.md)

## FastVLM PyTorch family

The 0.5B, 1.5B and 7B checkpoints share FastViTHD image encoding and connect the resulting image embeddings to the Qwen2 language model through a multimodal projector. Their stages identify published checkpoint variants. The checkpoint configuration supplies vision resolution and image preprocessing settings. Inference sends token IDs, image tensors and original image dimensions to the model and decodes its generated token IDs. [Language model](../models/model/language_model/qwen_language.py) [Vision tower](../models/model/multimodal_encoder/mobileclip_encoder.py) [Image embedding and projection](../models/model/vision_architecture.py)

For Apple Silicon, the export workflow prepares the vision tower as Core ML and language model artifacts for MLX-VLM. The Xcode app consumes the Apple-format model. [Export](code/apple_silicon/README.md) [Xcode demo](../third_party/apple_demo/README.md)
