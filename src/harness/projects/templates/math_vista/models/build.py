"""Construct the configured MathVista service adapter for a bounded request."""

import os
from pathlib import Path

from openai import AzureOpenAI

from mathvista.runtime import configuration


def azure_model(args):
    required = ("endpoint", "key", "version", "model")
    missing = [name for name in required if not getattr(args, f"azure_openai_api_{name}" if name != "model" else "azure_openai_model")]
    if missing:
        raise ValueError("Configure the Azure OpenAI " + ", ".join(missing) + " before using this model.")

    from models.gpt import GPT_Model

    client = AzureOpenAI(
        azure_endpoint=args.azure_openai_api_endpoint,
        api_key=args.azure_openai_api_key,
        api_version=args.azure_openai_api_version,
        timeout=30,
        max_retries=0,
    )
    return GPT_Model(client=client, model=args.azure_openai_model, patience=1)


def qwen_weights(args):
    path = args.model_path or os.environ.get("MATHVISTA_QWEN_WEIGHTS")
    return Path(path).expanduser().resolve() if path else None


def qwen_model(args):
    weights = qwen_weights(args)
    if weights is None or not (weights / "config.json").is_file():
        raise ValueError("Set --model_path or MATHVISTA_QWEN_WEIGHTS to a local Qwen2.5-VL checkpoint directory.")
    from models.qwen_vision.model import QwenVisionModel

    config = configuration()["catalogs"]["model"]["qwen_vision"]
    return QwenVisionModel(weights, args.device, args.max_new_tokens, config["max_pixels"])


def generation_model_name(args):
    if args.model_path or args.model == "qwen_vision":
        return "qwen_vision"
    return args.azure_openai_model or args.model


def generation_model(args):
    name = generation_model_name(args)
    if name == "qwen_vision":
        return qwen_model(args)
    if name == "bard":
        key = args.key or os.environ.get("_BARD_API_KEY")
        if not key:
            raise ValueError("Set _BARD_API_KEY before generating responses with Bard.")
        from models.bard import Bard_Model

        return Bard_Model(key)
    if "claude" in name:
        key = args.key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("Set ANTHROPIC_API_KEY before generating responses with Claude.")
        from models.claude import Claude_Model

        return Claude_Model(name, key, patience=1)
    return azure_model(args)
