"""Check local retrieval through the public command with generated inputs and model weights."""

import json
import sys

import pytest
from transformers import BertConfig, BertForSequenceClassification, BertModel, BertTokenizerFast


def write_jsonl(path, rows):
    path.write_text("".join(f"{json.dumps(row)}\n" for row in rows), encoding="utf-8")


@pytest.fixture
def tiny_bert(tmp_path):
    model_dir = tmp_path / "tiny-bert"
    model_dir.mkdir()
    vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]", "red", "apple", "blue", "sky"]
    vocab_path = model_dir / "vocab.txt"
    vocab_path.write_text("\n".join(vocab) + "\n", encoding="utf-8")
    BertTokenizerFast(str(vocab_path)).save_pretrained(model_dir)
    BertModel(BertConfig(
        vocab_size=len(vocab), hidden_size=16, num_hidden_layers=1,
        num_attention_heads=2, intermediate_size=24,
    )).save_pretrained(model_dir)
    return model_dir


@pytest.fixture
def custom_evaluation():
    pytest.importorskip("faiss")
    pytest.importorskip("pytrec_eval")
    from FlagEmbedding.evaluation.custom.__main__ import main

    return main


def test_custom_evaluation_disambiguates_query_ids_across_splits(custom_evaluation, tiny_bert, tmp_path, monkeypatch):
    dataset = tmp_path / "data" / "sample"
    dataset.mkdir(parents=True)
    documents = {"red": "red apple", "blue": "blue sky"}
    write_jsonl(dataset / "corpus.jsonl", [{"id": name, "text": text} for name, text in documents.items()])
    for split, document_id in (("test", "red"), ("dev", "blue")):
        write_jsonl(dataset / f"{split}_queries.jsonl", [{"id": "query", "text": documents[document_id]}])
        write_jsonl(dataset / f"{split}_qrels.jsonl", [{"qid": "query", "docid": document_id, "relevance": 1}])

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "FlagEmbedding.evaluation.custom", "--dataset_dir", "data", "--dataset_names", "sample",
        "--splits", "test", "dev", "--embedder_name_or_path", str(tiny_bert),
        "--embedder_model_class", "encoder-only-base", "--pooling_method", "mean",
        "--devices", "cpu", "--cache_path", "cache", "--output_dir", "search_results",
        "--search_top_k", "1", "--k_values", "1", "--eval_output_method", "json",
        "--eval_output_path", "report.json",
    ])
    custom_evaluation()
    assert json.loads((tmp_path / "report.json").read_text())["tiny-bert"]["NoReranker"]["sample-dev"]["recall_at_1"] == 1
    output_path = tmp_path / "search_results" / "tiny-bert" / "NoReranker"
    for split, document_id in (("test", "red"), ("dev", "blue")):
        result = json.loads((output_path / f"sample-{split}.json").read_text())
        assert result["eval_name"] == "custom"
        assert list(result["search_results"]["query"]) == [document_id]

    from FlagEmbedding.abc.evaluation import EvalDenseRetriever

    def unexpected_retrieval(*args, **kwargs):
        pytest.fail("Changing reporting cutoffs must reuse existing rankings")

    monkeypatch.setattr(EvalDenseRetriever, "__call__", unexpected_retrieval)
    sys.argv[sys.argv.index("--k_values") + 1] = "2"
    custom_evaluation()
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["tiny-bert"]["NoReranker"]["sample-dev"]["recall_at_2"] == 1


def test_custom_evaluation_rejects_missing_splits_before_loading_model(custom_evaluation, tmp_path, monkeypatch):
    corpus = tmp_path / "corpus.jsonl"
    write_jsonl(corpus, [{"id": "red", "text": "red apple"}])
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "FlagEmbedding.evaluation.custom", "--dataset_dir", str(tmp_path),
        "--embedder_name_or_path", "unavailable-local-model", "--splits", "dev",
    ])
    with pytest.raises(ValueError, match="No query and relevance file pair"):
        custom_evaluation()
    assert not (tmp_path / "search_results").exists()


def test_custom_precheck_reports_bad_input_without_writing_rankings(custom_evaluation, tiny_bert, tmp_path, monkeypatch, capsys):
    write_jsonl(tmp_path / "corpus.jsonl", [{"id": "red", "text": "red apple"}])
    write_jsonl(tmp_path / "test_queries.jsonl", [{"id": "query", "text": "red apple"}])
    judgments = tmp_path / "test_qrels.jsonl"
    write_jsonl(judgments, [{"qid": "query", "docid": "red", "relevance": 1}])
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "FlagEmbedding.evaluation.custom", "--dataset_dir", str(tmp_path),
        "--embedder_name_or_path", str(tiny_bert), "--embedder_model_class", "encoder-only-base",
        "--devices", "cpu", "--precheck_only",
    ])

    custom_evaluation()
    assert "Local retrieval precheck passed" in capsys.readouterr().out
    assert not (tmp_path / "search_results").exists()

    write_jsonl(judgments, [{"qid": "query", "docid": "red", "relevance": "bad grade"}])
    sys.argv.remove("--precheck_only")
    with pytest.raises(ValueError, match="Local retrieval precheck failed.*test_qrels.jsonl"):
        custom_evaluation()
    assert not (tmp_path / "search_results").exists()


def test_bright_excludes_documents_per_split(tiny_bert, tmp_path, monkeypatch):
    pytest.importorskip("faiss")
    pytest.importorskip("pytrec_eval")
    from FlagEmbedding.evaluation.bright.__main__ import main

    dataset = tmp_path / "data" / "biology"
    dataset.mkdir(parents=True)
    write_jsonl(dataset / "corpus.jsonl", [{"id": "red", "text": "red apple"}, {"id": "blue", "text": "blue sky"}])
    for split, relevant, excluded in (("examples", "red", "blue"), ("gpt4_reason", "blue", "red")):
        write_jsonl(dataset / f"{split}_queries.jsonl", [{"id": "query", "text": "blue apple"}])
        write_jsonl(dataset / f"{split}_qrels.jsonl", [
            {"qid": "query", "docid": relevant, "relevance": 1},
            {"qid": "query", "docid": excluded, "relevance": 0},
        ])

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "FlagEmbedding.evaluation.bright", "--eval_name", "bright", "--dataset_dir", "data",
        "--dataset_names", "biology", "--splits", "examples", "gpt4_reason",
        "--embedder_name_or_path", str(tiny_bert), "--embedder_model_class", "encoder-only-base",
        "--pooling_method", "mean", "--devices", "cpu", "--cache_path", "cache",
        "--output_dir", "search_results", "--search_top_k", "2", "--k_values", "1",
        "--eval_output_method", "json", "--eval_output_path", "report.json",
    ])
    search_top_k = sys.argv.index("--search_top_k") + 1
    sys.argv[search_top_k] = "0"
    with pytest.raises(ValueError, match="bright precheck failed.*search_top_k must be positive"):
        main()
    assert not (tmp_path / "search_results").exists()
    sys.argv[search_top_k] = "2"
    main()

    results = tmp_path / "search_results" / "tiny-bert" / "NoReranker"
    report = json.loads((tmp_path / "report.json").read_text())["tiny-bert"]["NoReranker"]
    for split, relevant in (("examples", "red"), ("gpt4_reason", "blue")):
        rankings = json.loads((results / f"biology-{split}.json").read_text())
        assert list(rankings["search_results"]["query"]) == [relevant]
        assert report[f"biology-{split}"]["recall_at_1"] == 1


def test_beir_separates_corpus_caches_and_reuses_rankings(tiny_bert, tmp_path, monkeypatch):
    pytest.importorskip("faiss")
    pytest.importorskip("pytrec_eval")
    pytest.importorskip("beir")
    from FlagEmbedding.abc.evaluation import EvalDenseRetriever, EvalReranker
    from FlagEmbedding.evaluation.beir import BEIREvalDataLoader
    from FlagEmbedding.evaluation.beir.__main__ import main

    # Exercise the official CQA layout with two generated members.
    def available_subsets(self, dataset_name):
        return ["android", "english"] if dataset_name == "cqadupstack" else None

    monkeypatch.setattr(BEIREvalDataLoader, "available_sub_dataset_names", available_subsets)
    for relative, text in (("arguana", "red apple"), ("cqadupstack/android", "blue sky"),
                           ("cqadupstack/english", "red sky")):
        dataset = tmp_path / "data" / relative
        dataset.mkdir(parents=True)
        write_jsonl(dataset / "corpus.jsonl", [{"id": relative, "text": text}])
        write_jsonl(dataset / "test_queries.jsonl", [{"id": "query", "text": text}])
        write_jsonl(dataset / "test_qrels.jsonl", [{"qid": "query", "docid": relative, "relevance": 1}])

    reranker_dir = tmp_path / "tiny-reranker"
    BertTokenizerFast.from_pretrained(tiny_bert).save_pretrained(reranker_dir)
    config = BertConfig.from_pretrained(tiny_bert, num_labels=1)
    BertForSequenceClassification(config).save_pretrained(reranker_dir)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [
        "FlagEmbedding.evaluation.beir", "--eval_name", "beir", "--dataset_dir", "data",
        "--dataset_names", "arguana", "cqadupstack", "--embedder_name_or_path", str(tiny_bert),
        "--embedder_model_class", "encoder-only-base", "--pooling_method", "mean",
        "--reranker_name_or_path", str(reranker_dir), "--reranker_model_class", "encoder-only-base",
        "--devices", "cpu", "--cache_path", "cache", "--corpus_embd_save_dir", "embeddings",
        "--output_dir", "search_results", "--search_top_k", "1", "--rerank_top_k", "1",
        "--k_values", "1", "--eval_output_method", "json", "--eval_output_path", "report.json",
    ])
    main()

    embedding_root = tmp_path / "embeddings" / "tiny-bert"
    assert {str(path.relative_to(embedding_root)) for path in embedding_root.rglob("doc.npy")} == {
        "arguana/doc.npy", "cqadupstack/android/doc.npy", "cqadupstack/english/doc.npy",
    }
    rankings_root = tmp_path / "search_results" / "tiny-bert"
    for stage in ("NoReranker", "tiny-reranker"):
        rankings = json.loads((rankings_root / stage / "cqadupstack-english-test.json").read_text())
        assert rankings["sub_dataset_name"] == "english"
        assert list(rankings["search_results"]["query"]) == ["cqadupstack/english"]
        regular = json.loads((rankings_root / stage / "arguana-test.json").read_text())
        assert regular["sub_dataset_name"] is None
        assert list(regular["search_results"]["query"]) == ["arguana"]

    def unexpected_search(*args, **kwargs):
        pytest.fail("The saved BEIR rankings should be reused")

    monkeypatch.setattr(EvalDenseRetriever, "__call__", unexpected_search)
    missing_reranking = rankings_root / "tiny-reranker" / "arguana-test.json"
    missing_reranking.unlink()
    main()
    assert missing_reranking.is_file()

    monkeypatch.setattr(EvalReranker, "__call__", unexpected_search)
    main()
    report = json.loads((tmp_path / "report.json").read_text())["tiny-bert"]
    for stage in ("NoReranker", "tiny-reranker"):
        assert report[stage]["arguana-test"]["recall_at_1"] == 1
        assert report[stage]["cqadupstack-test"]["recall_at_1"] == 1
