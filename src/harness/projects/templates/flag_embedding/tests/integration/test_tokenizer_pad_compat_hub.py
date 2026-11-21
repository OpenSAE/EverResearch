import os

import torch
from transformers import AutoTokenizer

from FlagEmbedding.utils.tokenizer_compat import pad_with_compat


RERANKER_MODEL_NAME = os.environ.get(
    "FLAGEMBEDDING_RERANKER_MODEL",
    "BAAI/bge-reranker-base",
)
ENCODER_MODEL_NAME = os.environ.get(
    "FLAGEMBEDDING_ENCODER_MODEL",
    "BAAI/bge-base-en-v1.5",
)


def test_local_bge_reranker_tokenizer_padding_compatibility():
    tokenizer = AutoTokenizer.from_pretrained(
        RERANKER_MODEL_NAME,
    )
    encoded = tokenizer(
        ["What is AI?", "Explain artificial intelligence in one sentence."],
        truncation=True,
        padding=False,
        return_tensors=None,
    )
    records = [
        {key: encoded[key][index] for key in encoded.keys()}
        for index in range(2)
    ]

    padded = pad_with_compat(
        tokenizer,
        records,
        padding=True,
        return_tensors="pt",
    )

    assert padded["input_ids"].shape[0] == 2
    assert padded["attention_mask"].shape == padded["input_ids"].shape
    assert torch.all(padded["attention_mask"][:, 0] == 1)


def test_local_bge_encoder_token_type_ids_are_preserved():
    tokenizer = AutoTokenizer.from_pretrained(
        ENCODER_MODEL_NAME,
    )
    encoded = tokenizer(
        ["short text", "a longer text for padding"],
        truncation=True,
        padding=False,
        return_tensors=None,
    )
    records = [
        {key: encoded[key][index] for key in encoded.keys()}
        for index in range(2)
    ]

    padded = pad_with_compat(
        tokenizer,
        records,
        padding=True,
        return_tensors="pt",
    )

    assert "token_type_ids" in padded
    assert padded["token_type_ids"].shape == padded["input_ids"].shape
    assert padded["attention_mask"].shape == padded["input_ids"].shape
