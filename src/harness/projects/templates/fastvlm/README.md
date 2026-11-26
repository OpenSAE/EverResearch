# FastVLM: Efficient Vision Encoding for Vision Language Models

> This template includes source code, configuration, and documentation. Obtain example inputs, pretrained weights, and media from the upstream project and set local paths before running resource-dependent examples.

> Upstream repository: [GitHub](https://github.com/apple-aiml-research/ml-fastvlm).

This is the official repository of
**[FastVLM: Efficient Vision Encoding for Vision Language Models](https://www.arxiv.org/abs/2412.13303). (CVPR 2025)**

[//]: # (![FastViTHD Performance]&#40;assets/documentation/figures/files/acc_vs_latency_qwen-2.png&#41;)
<p align="center">
<img src="assets/documentation/figures/files/acc_vs_latency_qwen-2.png" alt="Accuracy vs latency figure." width="400"/>
</p>

### Highlights
* We introduce FastViTHD, a novel hybrid vision encoder designed to output fewer tokens and significantly reduce encoding time for high-resolution images.  
* Our smallest variant outperforms LLaVA-OneVision-0.5B with 85x faster Time-to-First-Token (TTFT) and 3.4x smaller vision encoder.
* Our larger variants using Qwen2-7B LLM outperform recent works like Cambrian-1-8B while using a single image encoder with a 7.9x faster TTFT.
* Demo iOS app to demonstrate the performance of our model on a mobile device.

<table>
<tr>
    <td><img src="assets/documentation/figures/files/fastvlm-counting.gif" alt="FastVLM - Counting"></td>
    <td><img src="assets/documentation/figures/files/fastvlm-handwriting.gif" alt="FastVLM - Handwriting"></td>
    <td><img src="assets/documentation/figures/files/fastvlm-emoji.gif" alt="FastVLM - Emoji"></td>
</tr>
</table>

## Getting Started
We use LLaVA codebase to train FastVLM variants. In order to train or finetune your own variants, 
please follow instructions provided in [LLaVA](https://github.com/haotian-liu/LLaVA) codebase. 
We provide instructions for running inference with our models.   

### Setup
```bash
conda create -n fastvlm python=3.10
conda activate fastvlm
pip install -e .
```

### Model Zoo
For detailed information on various evaluations, please refer to our [paper](https://www.arxiv.org/abs/2412.13303).

| Model        | Stage |                                            Pytorch Checkpoint (url)                                             |
|:-------------|:-----:|:---------------------------------------------------------------------------------------------------------------:|
| FastVLM-0.5B |   2   | [fastvlm_0.5b_stage2](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_0.5b_stage2.zip) |
|              |   3   | [fastvlm_0.5b_stage3](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_0.5b_stage3.zip) |
| FastVLM-1.5B |   2   | [fastvlm_1.5b_stage2](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_1.5b_stage2.zip) |
|              |   3   | [fastvlm_1.5b_stage3](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_1.5b_stage3.zip)  |
| FastVLM-7B   |   2   | [fastvlm_7b_stage2](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_7b_stage2.zip)  |
|              |   3   | [fastvlm_7b_stage3](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_7b_stage3.zip)  |

To download all the pretrained checkpoints run the command below (note that this might take some time depending on your connection so might be good to grab ☕️ while you wait).

```bash
bash scripts/models/get_models.sh   # Downloads to data/fastvlm/checkpoints/
```

### Usage Example
To run inference of PyTorch checkpoint, follow the instruction below
```bash
python main.py --model-path /path/to/checkpoint-dir \
                  --image-file /path/to/image.png \
                  --prompt "Describe the image."
```

If you downloaded the 0.5B Stage 3 checkpoint into the workspace directory `data/fastvlm/checkpoints/`, you can omit `--model-path`. The command selects MPS, CUDA, or CPU in that order. Use `--device` to make the choice explicit. After installation, `fastvlm` accepts the same options.

Run `python main.py --show-config` to inspect defaults and overrides before loading a model. Use `--precheck --image-file /path/to/image.png` to check the selected model and image with a one-token probe. Inference runs this check automatically, prints the answer, and saves a manifest under `experiment/`. Read the result with `python main.py --read-result /path/to/metadata/manifest.json`. [Configuration and parameters](doc/conf.md) [Result layout and readback](doc/experiment.md)

The [project guide](doc/README.md) maps the Python package, model and data inputs, inference task, Apple demo, and maintenance checks.

### Inference on Apple Silicon
To run inference on Apple Silicon, pytorch checkpoints have to be exported to a format suitable for MLX and Core ML. Follow the [Apple Silicon export guide](doc/code/apple_silicon/README.md).

For convenience, we provide 3 models that are in Apple Silicon compatible format: [fastvlm_0.5b_stage3](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_0.5b_stage3_llm.fp16.zip), 
[fastvlm_1.5b_stage3](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_1.5b_stage3_llm.int8.zip), 
[fastvlm_7b_stage3](https://ml-site.cdn-apple.com/datasets/fastvlm/llava-fastvithd_7b_stage3_llm.int4.zip). 
We encourage developers to export the model of their choice with the appropriate quantization levels following 
the instructions in [Apple Silicon export guide](doc/code/apple_silicon/README.md).

### Inference on Apple Devices
To run inference on Apple devices like iPhone, iPad or Mac, see [Xcode demo](third_party/apple_demo/README.md) for more details.

## Citation
If you found this code useful, please cite the following paper:
```
@InProceedings{fastvlm2025,
  author = {Pavan Kumar Anasosalu Vasu, Fartash Faghri, Chun-Liang Li, Cem Koc, Nate True, Albert Antony, Gokul Santhanam, James Gabriel, Peter Grasch, Oncel Tuzel, Hadi Pouransari},
  title = {FastVLM: Efficient Vision Encoding for Vision Language Models},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  month = {June},
  year = {2025},
}
```

## Acknowledgements
Our codebase is built using multiple opensource contributions, please see [ACKNOWLEDGEMENTS](assets/licensing/upstream/files/ACKNOWLEDGEMENTS) for more details.

## License
Please check out the repository [LICENSE](LICENSE) before using the provided code and
[LICENSE_MODEL](assets/licensing/upstream/files/LICENSE_MODEL) for the released models.
