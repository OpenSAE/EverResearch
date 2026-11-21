# FastVLM configuration

`python main.py --show-config` displays the checkpoint and settings that inference will use. Pass command options to override the recipe. Explicit local paths resolve from the caller's directory, and the default checkpoint resolves from the checkout. An existing `./llava-v1.5-13b` directory in the caller's directory retains the legacy fallback. The preview prints `auto` as the requested device, and a successful run records the selected device.

## conf

### config.json

The runtime reads this recipe for image-prompt inference. [Default recipe](../conf/config.json)

| Key | Recipe default | Command and effect |
| --- | --- | --- |
| `model_path` | `"data/checkpoints/llava-fastvithd_0.5b_stage3"` | `--model-path` selects a checkpoint directory or Hub repository. |
| `model_base` | `null` | `--model-base` supplies a base checkpoint for compatible LLaVA adapters. |
| `image_file` | `null` | `--image-file` supplies the required local image. One image is decoded as RGB. |
| `dataset` | `"user_image"` | `--dataset` records the source of that file and selects the first result directory. Use a lowercase name such as `coco_val`, with digits and single underscores allowed after the first letter. |
| `prompt` | `"Describe the image."` | `--prompt` sets the text presented to the model alongside the image. |
| `conv_mode` | `"qwen_2"` | `--conv-mode` selects a template from `llava.conversation.conv_templates`. Choose the template expected by the checkpoint. |
| `temperature` | `0.2` | `--temperature` controls sampling sharpness. Zero disables sampling. |
| `top_p` | `null` | `--top-p` or `--top_p` sets the cumulative probability for nucleus sampling. The explicit range is greater than zero through one. |
| `num_beams` | `1` | `--num-beams` or `--num_beams` selects how many beams generation tracks. |
| `max_new_tokens` | `256` | `--max-new-tokens` caps the number of generated tokens. |
| `device` | `"auto"` | `--device` selects `mps`, `cuda`, or `cpu`. Automatic selection tries MPS, then CUDA, then CPU. CPU uses 32-bit floating-point weights and GPUs use 16-bit floating-point weights. |
| `subname` | `"describe_image"` | `--subname` names the experiment by purpose using one to three lowercase English words joined by underscores. |

The installed `fastvlm` command also accepts these options. A wheel installation uses a recognized checkout when launched within it. To run from another directory, set `FASTVLM_WORKSPACE` to an existing directory for the default checkpoint and `experiment/` results. Preview, standalone precheck and readback can run without setting a workspace. Explicit input paths still resolve from the caller's directory.

The recipe's `catalogs` section supplies the central layout checker with the supported dataset and checkpoint result group names. The configuration preview displays the options consumed by inference.

### models

#### model

##### config.json

The MobileCLIP encoder reads this file for its architecture and image embedding shape. The image settings declare the default 1024-pixel input, a 64-pixel patch and 3072 features per embedding. The checkpoint's configured vision tower supplies the input resolution used at runtime. [Encoder settings](../conf/models/model/config.json) [Encoder loader](../models/model/multimodal_encoder/mobileclip_encoder.py)
