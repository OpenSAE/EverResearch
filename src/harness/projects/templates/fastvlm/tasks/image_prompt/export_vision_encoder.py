#
# For licensing see accompanying LICENSE file.
# Copyright (C) 2025 Apple Inc. All Rights Reserved.
#
import os
import json
import copy
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory


def ensure_image_token(tokenizer_config):
    """Return the ID of the image marker and add it if the checkpoint needs one."""
    added_tokens = tokenizer_config["added_tokens_decoder"]
    for token_id, token in added_tokens.items():
        if token["content"] == "<image>":
            return int(token_id), False

    if not added_tokens:
        raise ValueError("The checkpoint tokenizer must define an added token to use as a template.")

    token_id = max(map(int, added_tokens)) + 1
    token = copy.deepcopy(next(iter(added_tokens.values())))
    token["content"] = "<image>"
    added_tokens[str(token_id)] = token
    return token_id, True


def export(args):
    from fastvlm.tasks.precheck import check_export_checkpoint

    check_export_checkpoint(args.model_path, args.model_base)
    import torch
    import numpy as np
    import coremltools
    from llava.model.builder import load_pretrained_model
    from llava.utils import disable_torch_init
    from llava.mm_utils import get_model_name_from_path

    # Load model
    disable_torch_init()
    model_path = os.path.expanduser(args.model_path)
    model_name = get_model_name_from_path(model_path)
    tokenizer, model, image_processor, context_len = load_pretrained_model(model_path,
                                                                           args.model_base,
                                                                           model_name,
                                                                           device="mps")

    # Save extra metadata that is not saved during LLaVA training
    # required by HF for auto-loading model and for mlx-vlm preprocessing

    # Save image processing config
    setattr(image_processor, "processor_class", "LlavaProcessor")
    output_path = os.path.join(model_path, "preprocessor_config.json")
    image_processor.to_json_file(output_path)

    # Create processor config
    processor_config = dict()
    processor_config["image_token"] = "<image>"
    processor_config["num_additional_image_tokens"] = 0
    processor_config["processor_class"] = "LlavaProcessor"
    processor_config["patch_size"] = 64
    output_path = os.path.join(model_path, "processor_config.json")
    json.dump(processor_config, open(output_path, "w"), indent=2)

    # Reuse the checkpoint's image token ID when exporting it again.
    tokenizer_config_path = Path(model_path) / "tokenizer_config.json"
    tokenizer_config = json.loads(tokenizer_config_path.read_text(encoding="utf-8"))
    image_token_id, token_added = ensure_image_token(tokenizer_config)
    if token_added:
        tokenizer_config_path.write_text(json.dumps(tokenizer_config, indent=2), encoding="utf-8")

    # Modify config to contain token id for <image>
    config_path = Path(model_path) / "config.json"
    model_config = json.loads(config_path.read_text(encoding="utf-8"))
    model_config["image_token_index"] = image_token_id
    config_path.write_text(json.dumps(model_config, indent=2), encoding="utf-8")

    # Export the vision encoder to CoreML
    image_res = image_processor.to_dict()['size']['shortest_edge']
    inputs = torch.rand(1, 3, image_res, image_res)
    inputs_tensor = [
        coremltools.TensorType(
            name="images",
            shape=inputs.shape,
        )
    ]
    vision_model = model.get_vision_tower()
    vision_model = vision_model.float()
    traced_model = torch.jit.trace(vision_model, torch.Tensor(inputs))
    with TemporaryDirectory(prefix="fastvlm-vision-") as temporary:
        traced_path = str(Path(temporary) / "fastvithd.pt")
        traced_model.save(traced_path)

        ml_model = coremltools.convert(
            model=traced_path,
            outputs=[coremltools.TensorType(name="image_features", dtype=np.float32)],
            inputs=inputs_tensor,
            convert_to="mlprogram",
            debug=False,
            compute_units=coremltools.ComputeUnit.CPU_AND_GPU,
            minimum_deployment_target=coremltools.target.iOS16,
            compute_precision=coremltools.precision.FLOAT32
        )
        ml_model_path = os.path.join(model_path, "fastvithd.mlpackage")
        ml_model.save(ml_model_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, required=True)
    parser.add_argument("--model-base", type=str, default=None)
    parser.add_argument("--conv-mode", type=str, default="qwen_2")

    args = parser.parse_args()

    try:
        export(args)
    except (OSError, ValueError) as error:
        parser.error(str(error))
