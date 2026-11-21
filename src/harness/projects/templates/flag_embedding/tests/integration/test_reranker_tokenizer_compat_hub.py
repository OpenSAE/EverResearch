import os

import pytest
from packaging.version import Version
from types import SimpleNamespace

from transformers import AutoTokenizer

from FlagEmbedding.abc.finetune.reranker.AbsDataset import AbsRerankerTrainDataset
from FlagEmbedding.utils.tokenizer_compat import prepare_for_model_compat


RERANKER_MODEL_NAME = os.environ.get(
    "FLAGEMBEDDING_RERANKER_MODEL",
    "BAAI/bge-reranker-base",
)


def test_encoder_pair_preserves_v5_tokenizer_input_ids(transformers_version):
    if transformers_version < Version("5"):
        pytest.skip("Tokenizers expose prepare_for_model on Transformers 4.x.")
    tokenizer = AutoTokenizer.from_pretrained(
        RERANKER_MODEL_NAME,
    )

    query = "😀🧪"
    passage = "unknown token"
    query_ids = tokenizer(query, add_special_tokens=False)["input_ids"]
    passage_ids = tokenizer(passage, add_special_tokens=False)["input_ids"]

    actual = prepare_for_model_compat(
        tokenizer,
        query_ids,
        passage_ids,
        truncation="only_second",
        max_length=64,
        padding=False,
    )
    expected = tokenizer(
        query,
        passage,
        truncation="only_second",
        max_length=64,
        padding=False,
    )

    assert not hasattr(tokenizer, "prepare_for_model")
    assert actual["input_ids"] == expected["input_ids"]
    assert actual["attention_mask"] == expected["attention_mask"]


def test_encoder_training_example_works_without_prepare_for_model():
    tokenizer = AutoTokenizer.from_pretrained(
        RERANKER_MODEL_NAME,
    )
    dataset = AbsRerankerTrainDataset.__new__(AbsRerankerTrainDataset)
    dataset.tokenizer = tokenizer
    dataset.args = SimpleNamespace(query_max_len=32, passage_max_len=128)

    actual = dataset.create_one_example("What is AI?", "AI is artificial intelligence.")
    expected = tokenizer(
        "What is AI?",
        "AI is artificial intelligence.",
        truncation="only_second",
        max_length=160,
        padding=False,
    )

    assert actual["input_ids"] == expected["input_ids"]
    assert actual["attention_mask"] == expected["attention_mask"]
