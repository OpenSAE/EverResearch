# Local Qwen vision and language model

## Purpose and main function

Run the official Qwen2.5-VL-3B-Instruct checkpoint for MathVista image-text
generation and text-only answer extraction.

## Scope of application

The generation and extraction commands use this adapter when the local Qwen
model is selected. It uses the project's pinned vision pixel budget,
deterministic one-item decoding, and an explicit checkpoint directory.
[Checkpoint and environment setup](../../doc/environment/README.md#local-qwen-weights)
