# Steamboat Willie fine-tuning split

## Purpose and main function

Keep the three held-out clip positions used in the formal Diffusers fine-tuning recipe. The other 66 clips form its training split.

## Scope of application

Positions count from one in the unchanged paired `prompt.txt` and `videos.txt` files of the publisher's 69-clip snapshot `823c1f015e7ced7fffb8ad44881f792195114386`. This project split uses samples spaced across the published list for validation previews. The [formal run guide](../../../doc/experiment/formal_runs.md) gives preparation commands. [Publisher dataset](https://huggingface.co/datasets/Wild-Heart/Disney-VideoGeneration-Dataset/tree/823c1f015e7ced7fffb8ad44881f792195114386)
