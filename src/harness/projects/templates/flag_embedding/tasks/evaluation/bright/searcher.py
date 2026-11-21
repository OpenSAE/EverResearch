"""Apply BRIGHT's document exclusions to the shared dense search results."""

import logging
from typing import Any, Dict, Optional

from FlagEmbedding.abc.evaluation import EvalDenseRetriever

logger = logging.getLogger(__name__)


class BrightEvalDenseRetriever(EvalDenseRetriever):
    """Filter benchmark exclusions from the retrieved candidates for each query."""

    def __call__(
        self,
        corpus: Dict[str, Dict[str, Any]],
        queries: Dict[str, str],
        corpus_embd_save_dir: Optional[str] = None,
        ignore_identical_ids: bool = False,
        **kwargs,
    ) -> Dict[str, Dict[str, float]]:
        qrels = kwargs.pop("retriever_qrels", None)
        if qrels is None:
            logger.warning("No qrels provided, so no documents will be excluded.")

        results = super().__call__(
            corpus=corpus,
            queries=queries,
            corpus_embd_save_dir=corpus_embd_save_dir,
            ignore_identical_ids=ignore_identical_ids,
            **kwargs,
        )
        for query_id, candidates in results.items():
            if qrels is not None:
                for doc_id, relevance in qrels[query_id].items():
                    if relevance != 1 and doc_id != "N/A":
                        candidates.pop(doc_id, None)
            results[query_id] = dict(sorted(candidates.items(), key=lambda item: item[1], reverse=True))
        return results
