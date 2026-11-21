"""Load Transformers models and tokenizers used by the public compressor."""

import torch
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForTokenClassification,
    AutoTokenizer,
)


def load_compressor_model(model_name, device_map, model_config):
    options = dict(model_config)
    options.setdefault("trust_remote_code", True)
    pad_to_left = options.pop("pad_to_left", True)
    config = AutoConfig.from_pretrained(model_name, **options)
    tokenizer = AutoTokenizer.from_pretrained(model_name, **options)
    if pad_to_left:
        tokenizer.padding_side = "left"
        tokenizer.pad_token_id = (
            tokenizer.eos_token_id
            if config.pad_token_id is None
            else config.pad_token_id
        )
    model_class = (
        AutoModelForTokenClassification
        if any(
            "ForTokenClassification" in name for name in (config.architectures or ())
        )
        else AutoModelForCausalLM
    )
    direct_device = "cuda" in device_map or "cpu" in device_map
    default_dtype = torch.float32 if direct_device and device_map != "cuda" else "auto"
    options.setdefault("torch_dtype", default_dtype)
    if direct_device:
        options.update(config=config, ignore_mismatched_sizes=True)
    else:
        options["pad_token_id"] = tokenizer.pad_token_id
    model = model_class.from_pretrained(model_name, device_map=device_map, **options)
    device = (
        device_map
        if any(key in device_map for key in ("cuda", "cpu", "mps"))
        else "cuda"
    )
    return model, tokenizer, config, device


def load_training_classifier(model_name):
    """Load the tokenizer and two-class Transformer used by both trainers."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(
        model_name, num_labels=2, ignore_mismatched_sizes=True
    )
    return model, tokenizer
