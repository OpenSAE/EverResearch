"""Check retrieval and reranking on one query and document before full evaluation."""

from copy import copy
import json
from math import isfinite
from pathlib import Path
from tempfile import TemporaryDirectory


def first_record(path, fields):
    with path.open(encoding="utf-8") as source:
        line = next((line for line in source if line.strip()), None)
    if line:
        try:
            row = json.loads(line)
        except ValueError as error:
            raise ValueError(f"Invalid JSON in {path}: {error}") from error
        if isinstance(row, dict) and all(key in row and isinstance(row[key], kind) for key, kind in fields.items()):
            return row
    raise ValueError(f"{path} must contain a record with {', '.join(fields)}")


def check_ranking(evaluator, split, dataset_options, model_name, reranker_name, rankings, query_id, document_id):
    with TemporaryDirectory(prefix="flagembedding-precheck-") as directory:
        path = Path(directory) / "ranking.json"
        evaluator.save_search_results(
            eval_name=evaluator.eval_name, model_name=model_name, reranker_name=reranker_name,
            search_results=rankings, output_path=path, split=split, **dataset_options,
        )
        metadata, readback = evaluator.load_search_results(path)
        evaluator.check_data_info(metadata, model_name, reranker_name, split, **dataset_options)
    score = readback.get(query_id, {}).get(document_id)
    if score is None or not isfinite(score):
        raise ValueError(f"{reranker_name} did not produce a finite score for the sampled query and document")


def check_retrieval_sample(evaluator, split, dataset_options, retriever, corpus, queries, *, ignore_identical_ids=False, **kwargs):
    query_id = next(iter(queries), None)
    if query_id is None:
        raise ValueError("the query split is empty")
    exclusions = kwargs.get("retriever_qrels")
    if exclusions is not None:
        judgments = exclusions.get(query_id)
        if judgments is None:
            raise ValueError(f"no document judgments for query {query_id!r}")
    else:
        judgments = {}
    eligible = (doc_id for doc_id in corpus if judgments.get(doc_id, 1) == 1 or doc_id == "N/A")
    document_id = next(eligible, None)
    if document_id is None:
        raise ValueError(f"no eligible document for sampled query {query_id!r}")
    if ignore_identical_ids and document_id == query_id:
        document_id = next(eligible, document_id)
    if retriever.search_top_k < 1:
        raise ValueError("search_top_k must be positive")

    sample_retriever = copy(retriever)
    sample_retriever.search_top_k = 1
    rankings = sample_retriever(
        corpus={document_id: corpus[document_id]}, queries={query_id: queries[query_id]},
        ignore_identical_ids=ignore_identical_ids and query_id != document_id, **kwargs,
    )
    check_ranking(evaluator, split, dataset_options, str(retriever), "NoReranker", rankings, query_id, document_id)
    return rankings


def check_reranking_sample(
    evaluator, split, dataset_options, retriever, reranker, corpus, queries, rankings, *,
    ignore_identical_ids=False, **kwargs,
):
    pair = next(((query_id, doc_id, score) for query_id, docs in rankings.items() for doc_id, score in docs.items()), None)
    if pair is None:
        raise ValueError("the retrieved rankings are empty")
    if reranker.rerank_top_k < 1:
        raise ValueError("rerank_top_k must be positive")
    query_id, document_id, score = pair
    reranked = reranker(
        corpus={document_id: corpus[document_id]}, queries={query_id: queries[query_id]},
        search_results={query_id: {document_id: score}},
        ignore_identical_ids=ignore_identical_ids and query_id != document_id, **kwargs,
    )
    check_ranking(evaluator, split, dataset_options, str(retriever), str(reranker), reranked, query_id, document_id)


def check_retrieval(evaluator, dataset_dir, dataset_name, split, retriever, reranker, ignore_identical_ids, *, files_only=False):
    """Check local file structure and optionally score a single query and document."""
    try:
        document = first_record(dataset_dir / "corpus.jsonl", {"id": str, "text": str})
        query = first_record(dataset_dir / f"{split}_queries.jsonl", {"id": str, "text": str})
        first_record(dataset_dir / f"{split}_qrels.jsonl", {"qid": str, "docid": str, "relevance": int})
        if files_only:
            return
        corpus = {document["id"]: document}
        queries = {query["id"]: query["text"]}
        options = {"dataset_name": dataset_name}
        rankings = check_retrieval_sample(
            evaluator, split, options, retriever, corpus, queries, ignore_identical_ids=ignore_identical_ids,
        )
        if reranker is not None:
            check_reranking_sample(
                evaluator, split, options, retriever, reranker, corpus, queries, rankings,
                ignore_identical_ids=ignore_identical_ids,
            )
    except (OSError, ValueError) as error:
        raise ValueError(f"Local retrieval precheck failed for {dataset_dir} ({split}): {error}") from error
