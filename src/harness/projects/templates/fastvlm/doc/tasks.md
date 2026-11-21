# FastVLM tasks

## Use and entry points

Run the PyTorch image-prompt task with `python main.py` from a checkout or `fastvlm` after installation. The command accepts one local image, a model checkpoint and a prompt. It produces a text answer and a run manifest for later readback. [Run the task](../README.md#usage-example)

## Shared parameters

The recipe supplies the prompt, template and generation limits. Overrides are visible with `--show-config`. A normal run automatically validates the image, checkpoint and conversation template, generates one token, and verifies temporary result readback before starting formal generation. Use `--precheck` to run the check on its own. [Options and defaults](conf.md)

## Image-prompt inference

The task adds the image marker required by the checkpoint, builds the prompt with the selected LLaVA conversation template, and applies the checkpoint image processor. It calls the model's generation interface, decodes the answer and records it with input identity. This task produces generated text as its result. It defines no accuracy or latency metric. [Generation implementation](../tasks/image_prompt/__init__.py) [Readback](experiment.md)

## Adjacent workstreams

The inherited LLaVA commands include interactive chat (`llava.serve.cli`), serving (controller, workers and Gradio), and training (`llava.train.train`, `llava.train.train_mem`, `llava.train.train_qwen`, `llava.train.train_xformers`). Interactive chat checks the checkpoint path, conversation template and input image before opening the conversation. The PyTorch worker validates local checkpoint paths before loading and both generation workers validate and decode image attachments before generating text. The checked-in worker message client `llava.serve.worker_message` is a live-service probe. [Serving package](../tasks/serve/)

Training checks the paths before it loads the model, then reads and collates the first sample before starting the trainer. The check requires at least one target token after tokenization and verifies that an image sample can reach the vision tower. The chosen launcher retains its native training options and caller-selected output directory. The project README points training users to the upstream LLaVA recipes. [Training package](../tasks/train/) [Training data reader](../datasets/supervised/__init__.py)

The Apple-device demo captures camera frames and provides selected prompts and time to first token in the interface. Apple Silicon export checks the local checkpoint metadata and PyTorch MPS availability before conversion. The export workflow produces artifacts for the demo or MLX-VLM. [App](../third_party/apple_demo/README.md) [Export](code/apple_silicon/README.md)
