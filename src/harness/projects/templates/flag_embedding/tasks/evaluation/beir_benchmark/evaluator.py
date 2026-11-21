import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, List, Union

from FlagEmbedding.abc.evaluation import AbsEvaluator, EvalRetriever, EvalReranker

logger = logging.getLogger(__name__)


class BEIREvaluator(AbsEvaluator):
    """
    Evaluator class of BEIR 
    """
    def check_data_info(
        self,
        data_info: Dict[str, str],
        model_name: str,
        reranker_name: str,
        split: str,
        dataset_name: Optional[str] = None,
        sub_dataset_name: Optional[str] = None,
    ):
        """Check the validity of data info.

        Args:
            data_info (Dict[str, str]): The loaded data info to be check.
            model_name (str): Name of model used.
            reranker_name (str): Name of reranker used.
            split (str): Split used in searching.
            dataset_name (Optional[str], optional): Name of dataset used. Defaults to None.
            sub_dataset_name (Optional[str], optional): Name of the sub-dataset. Defaults to ``None``.

        Raises:
            ValueError: eval_name mismatch
            ValueError: model_name or reranker_name mismatch
            ValueError: split mismatch
            ValueError: dataset_name mismatch
            ValueError: sub_dataset_name mismatch
        """
        super().check_data_info(data_info, model_name, reranker_name, split, dataset_name)
        if sub_dataset_name is not None and data_info["sub_dataset_name"] != sub_dataset_name:
            raise ValueError(
                f'sub_dataset_name mismatch: {data_info["sub_dataset_name"]} vs {sub_dataset_name}'
            )

    def __call__(
        self,
        splits: Union[str, List[str]],
        search_results_save_dir: str,
        retriever: EvalRetriever,
        reranker: Optional[EvalReranker] = None,
        corpus_embd_save_dir: Optional[str] = None,
        ignore_identical_ids: bool = False,
        k_values: List[int] = [1, 3, 5, 10, 100, 1000],
        dataset_name: Optional[str] = None,
        **kwargs,
    ):
        checked_splits = self.data_loader.check_splits(splits, dataset_name=dataset_name)
        if not checked_splits:
            logger.warning(f"{splits} not found in the dataset. Skipping evaluation.")
            return

        sub_datasets = self.data_loader.available_sub_dataset_names(dataset_name=dataset_name)
        results_dir = Path(search_results_save_dir) / str(retriever)
        retrieval_dir = results_dir / "NoReranker"
        retrieval_changed = False
        reranking_changed = False
        for sub_dataset_name in sub_datasets or [None]:
            dataset_options = {"dataset_name": dataset_name}
            if sub_dataset_name is not None:
                dataset_options["sub_dataset_name"] = sub_dataset_name

            names = [name for name in (dataset_name, sub_dataset_name) if name is not None]
            save_name = "-".join([*names, "{split}.json"])
            corpus_cache = corpus_embd_save_dir
            if corpus_cache is not None and dataset_name is not None:
                corpus_cache = os.path.join(corpus_cache, str(retriever), *names)

            rankings, changed = self._retrieve_splits(
                checked_splits, retrieval_dir, save_name, retriever, corpus_cache,
                ignore_identical_ids, dataset_options, reranker=reranker, **kwargs,
            )
            retrieval_changed |= changed
            if sub_dataset_name is None:
                retriever.stop_multi_process_pool()

            if reranker is not None:
                reranker_dir = results_dir / str(reranker)
                reranking_changed |= self._rerank_splits(
                    checked_splits, reranker_dir, save_name, retriever, reranker, rankings,
                    ignore_identical_ids, dataset_options, rankings_changed=changed, **kwargs,
                )

        if sub_datasets:
            retriever.stop_multi_process_pool()
        self._write_metrics(retrieval_dir, k_values, retrieval_changed)
        if reranker is not None:
            reranker.stop_multi_process_pool()
            self._write_metrics(reranker_dir, k_values, reranking_changed)

    def evaluate_results(
        self,
        search_results_save_dir: str,
        k_values: List[int] = [1, 3, 5, 10, 100, 1000]
    ):
        """Compute metrics according to the results in the directory.

        Args:
            search_results_save_dir (str): Path to the search results.
            k_values (List[int], optional): Cutoffs. Defaults to :data:`[1, 3, 5, 10, 100, 1000]`.

        Returns:
            dict: Evaluation results.
        """
        eval_results_dict = {}
        cqadupstack_results = None
        cqadupstack_num = 0

        for file in os.listdir(search_results_save_dir):
            if not file.endswith('.json'):
                continue

            file_path = os.path.join(search_results_save_dir, file)
            data_info, search_results = self.load_search_results(file_path)

            _eval_name = data_info['eval_name']
            assert _eval_name == self.eval_name, f'Mismatch eval_name: {_eval_name} vs {self.eval_name} in {file_path}'

            split = data_info['split']
            dataset_name = data_info.get('dataset_name', None)
            sub_dataset_name = data_info.get('sub_dataset_name', None)
            qrels = self.data_loader.load_qrels(dataset_name=dataset_name, sub_dataset_name=sub_dataset_name, split=split)

            eval_results = self.compute_metrics(
                qrels=qrels,
                search_results=search_results,
                k_values=k_values
            )

            if dataset_name is not None:
                if sub_dataset_name is None:
                    key = f"{dataset_name}-{split}"
                else:
                    key = f"{dataset_name}-{sub_dataset_name}-{split}"
            else:
                if sub_dataset_name is None:
                    key = split
                else:
                    key = f"{sub_dataset_name}-{split}"
            if sub_dataset_name is None:
                eval_results_dict[key] = eval_results
            else:
                if cqadupstack_results is None:
                    cqadupstack_results = eval_results
                    cqadupstack_num += 1
                else:
                    for k, v in eval_results.items():
                        cqadupstack_results[k] += v
                    cqadupstack_num += 1
        
        if cqadupstack_num > 0:
            for k in cqadupstack_results.keys():
                cqadupstack_results[k] /= cqadupstack_num
            eval_results_dict['cqadupstack-test'] = cqadupstack_results

        return eval_results_dict
    
    def save_search_results(
        self,
        eval_name: str,
        model_name: str,
        reranker_name: str,
        search_results: Dict[str, Dict[str, float]],
        output_path: str,
        split: str,
        dataset_name: Optional[str] = None,
        sub_dataset_name: Optional[str] = None,
    ):
        """Save the metadata and search results into a file.

        Args:
            eval_name (str): The experiment name of current evaluation.
            model_name (str): Name of model used.
            reranker_name (str): Name of reranker used.
            search_results (Dict[str, Dict[str, float]]): Dictionary of search results.
            output_path (str): Output path to write the results.
            split (str): Split used in searching.
            dataset_name (Optional[str], optional): Name of dataset used. Defaults to ``None``.
            sub_dataset_name (Optional[str], optional): Name of the sub-dataset. Defaults to ``None``.
        """
        data = {
            "eval_name": eval_name,
            "model_name": model_name,
            "reranker_name": reranker_name,
            "split": split,
            "dataset_name": dataset_name,
            "sub_dataset_name": sub_dataset_name,
            "search_results": search_results,
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
