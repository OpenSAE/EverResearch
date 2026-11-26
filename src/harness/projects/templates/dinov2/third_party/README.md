# Third-party source and upstream entry points

## Purpose and main function

Keep the vendored OpenAI CLIP tokenizer and the original DINOv2 PyTorch Hub entry file.

## Scope of application

The installed DINOv2 package uses the [CLIP tokenizer](clip) for image-text workflows.
[PyTorch Hub](pytorch_hub) uses its fixed `hubconf.py` filename when loading this checkout as
a local Hub repository. Install DINOv2 before calling that interface.
