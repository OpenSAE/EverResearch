"""Decoder-only reranking examples shared by the direct and automatic launchers."""

from os import getenv

from FlagEmbedding import FlagAutoReranker, FlagLLMReranker, LayerWiseFlagLLMReranker, LightWeightFlagLLMReranker


PAIRS = [
    ['What is the capital of France?', 'Paris is the capital of France.'],
    ['What is the capital of France?', 'The population of China is over 1.4 billion people.'],
    ['What is the population of China?', 'Paris is the capital of France.'],
    ['What is the population of China?', 'The population of China is over 1.4 billion people.'],
]


def _show_scores(load, model_name, devices, *, scoring=None, **model_options):
    model = load(
        model_name,
        use_fp16=True,
        query_instruction_for_rerank="A: ",
        passage_instruction_for_rerank="B: ",
        devices=devices,
        cache_dir=getenv("HF_HUB_CACHE"),
        **model_options,
    )
    scores = model.compute_score(PAIRS * 100, **(scoring or {}))
    print(scores[:4])


def show_base(devices, *, automatic):
    load = FlagAutoReranker.from_finetuned if automatic else FlagLLMReranker
    _show_scores(load, "BAAI/bge-reranker-v2-gemma", devices)


def show_layerwise(devices, *, automatic):
    load = FlagAutoReranker.from_finetuned if automatic else LayerWiseFlagLLMReranker
    _show_scores(
        load,
        "BAAI/bge-reranker-v2-minicpm-layerwise",
        devices,
        scoring={"cutoff_layers": [28]},
        trust_remote_code=True,
    )


def show_lightweight(devices, *, automatic):
    load = FlagAutoReranker.from_finetuned if automatic else LightWeightFlagLLMReranker
    _show_scores(
        load,
        "BAAI/bge-reranker-v2.5-gemma2-lightweight",
        devices,
        scoring={"cutoff_layers": [28], "compress_ratio": 2, "compress_layers": [24, 40]},
        trust_remote_code=True,
    )
