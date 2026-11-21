"""
Adapted from https://github.com/AIR-Bench/AIR-Bench/blob/0.1.0/air_benchmark/evaluation_utils/evaluator.py
"""
import json
import logging
import os
from pathlib import Path
import pandas as pd
from typing import Dict, Optional, List, Union

from FlagEmbedding.precheck.retrieval import check_retrieval_sample, check_reranking_sample

from ..data_loader import AbsEvalDataLoader
from ..searcher import EvalRetriever, EvalReranker
from ..utils import evaluate_metrics, evaluate_mrr, evaluate_recall_cap

logger = logging.getLogger(__name__)


class AbsEvaluator:
    """
    Base class of Evaluator.
    
    Args:
        eval_name (str): The experiment name of current evaluation.
        data_loader (AbsEvalDataLoader): The data_loader to deal with data.
        overwrite (bool): If true, will overwrite the existing results.
    """
    def __init__(
        self,
        eval_name: str,
        data_loader: AbsEvalDataLoader,
        overwrite: bool = False,
    ):
        self.eval_name = eval_name
        self.data_loader = data_loader
        self.overwrite = overwrite

    def check_data_info(
        self,
        data_info: Dict[str, str],
        model_name: str,
        reranker_name: str,
        split: str,
        dataset_name: Optional[str] = None,
    ):
        """Check the validity of data info.

        Args:
            data_info (Dict[str, str]): The loaded data info to be check.
            model_name (str): Name of model used.
            reranker_name (str): Name of reranker used.
            split (str): Split used in searching.
            dataset_name (Optional[str], optional): Name of dataset used. Defaults to None.

        Raises:
            ValueError: eval_name mismatch
            ValueError: model_name or reranker_name mismatch
            ValueError: split mismatch
            ValueError: dataset_name mismatch
        """
        if data_info["eval_name"] != self.eval_name:
            raise ValueError(
                f'eval_name mismatch: {data_info["eval_name"]} vs {self.eval_name}'
            )
        if (
            data_info["model_name"] != model_name
            or data_info["reranker_name"] != reranker_name
        ):
            raise ValueError(
                f'model_name or reranker_name mismatch: {data_info["model_name"]} vs {model_name} or {data_info["reranker_name"]} vs {reranker_name}'
            )
        if (data_info["split"] != split):
            raise ValueError(
                f'split mismatch: {data_info["split"]} vs {split}'
            )
        if dataset_name is not None and data_info["dataset_name"] != dataset_name:
            raise ValueError(
                f'dataset_name mismatch: {data_info["dataset_name"]} vs {dataset_name}'
            )

    def get_corpus_embd_save_dir(
        self,
        retriever_name: str,
        corpus_embd_save_dir: Optional[str] = None,
        dataset_name: Optional[str] = None
    ):
        """
        If corpus_embd_save_dir is not None, then it will be used as the base directory to save the corpus embeddings. For dataset such as MKQA, 
            the corpus for all languages is the same, so the subclass can override this method to save the corpus embeddings in the same directory.
        
        Args:
            retriever_name (str): Name of the retriever.
            corpus_embd_save_dir (str, optional): Directory that saving the corpus embedding.
            dataset_name (str, optional): 
        """
        if corpus_embd_save_dir is not None:
            if dataset_name is not None:
                corpus_embd_save_dir = os.path.join(corpus_embd_save_dir, retriever_name, dataset_name)
            else:
                corpus_embd_save_dir = os.path.join(corpus_embd_save_dir, retriever_name)
        return corpus_embd_save_dir

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
        """This is called during the evaluation process.

        Args:
            splits (Union[str, List[str]]): Splits of datasets.
            search_results_save_dir (str): Directory to save the search results.
            retriever (EvalRetriever): object of :class:EvalRetriever.
            reranker (Optional[EvalReranker], optional): Object of :class:EvalReranker. Defaults to :data:`None`.
            corpus_embd_save_dir (Optional[str], optional): Directory to save the embedded corpus. Defaults to :data:`None`.
            ignore_identical_ids (bool, optional): If True, will ignore identical ids in search results. Defaults to :data:`False`.
            k_values (List[int], optional): Cutoffs. Defaults to :data:`[1, 3, 5, 10, 100, 1000]`.
            dataset_name (Optional[str], optional): Name of the datasets. Defaults to :data:`None`.
        """
        # Check Splits
        checked_splits = self.data_loader.check_splits(splits, dataset_name=dataset_name)
        if len(checked_splits) == 0:
            logger.warning(f"{splits} not found in the dataset. Skipping evaluation.")
            return
        splits = checked_splits

        save_name = f"{dataset_name}-{{split}}.json" if dataset_name is not None else "{split}.json"
        corpus_embd_save_dir = self.get_corpus_embd_save_dir(
            retriever_name=str(retriever),
            corpus_embd_save_dir=corpus_embd_save_dir,
            dataset_name=dataset_name,
        )
        results_dir = Path(search_results_save_dir) / str(retriever)
        rankings, rankings_changed = self._retrieve_splits(
            splits, results_dir / "NoReranker", save_name, retriever,
            corpus_embd_save_dir, ignore_identical_ids, {"dataset_name": dataset_name}, reranker=reranker, **kwargs,
        )
        retriever.stop_multi_process_pool()
        self._write_metrics(results_dir / "NoReranker", k_values, rankings_changed)

        if reranker is not None:
            reranker_dir = results_dir / str(reranker)
            rerankings_changed = self._rerank_splits(
                splits, reranker_dir, save_name, retriever, reranker, rankings,
                ignore_identical_ids, {"dataset_name": dataset_name}, rankings_changed=rankings_changed, **kwargs,
            )
            reranker.stop_multi_process_pool()
            self._write_metrics(reranker_dir, k_values, rerankings_changed)

    def _retrieve_splits(
        self, splits, results_dir, save_name, retriever, corpus_embd_save_dir,
        ignore_identical_ids, dataset_options, *, reranker=None, **kwargs,
    ):
        result_paths = {split: results_dir / save_name.format(split=split) for split in splits}
        rankings = {}
        changed = self.overwrite or any(not path.exists() for path in result_paths.values())
        if not changed:
            for split, path in result_paths.items():
                data_info, rankings[split] = self.load_search_results(path)
                self.check_data_info(
                    data_info=data_info,
                    model_name=str(retriever),
                    reranker_name="NoReranker",
                    split=split,
                    **dataset_options,
                )
            return rankings, changed

        corpus = self.data_loader.load_corpus(**dataset_options)
        queries_by_split = {
            split: self.data_loader.load_queries(split=split, **dataset_options)
            for split in result_paths
        }
        for split, queries in queries_by_split.items():
            try:
                sample = check_retrieval_sample(
                    self, split, dataset_options, retriever, corpus, queries,
                    ignore_identical_ids=ignore_identical_ids, **kwargs,
                )
                if reranker is not None:
                    check_reranking_sample(
                        self, split, dataset_options, retriever, reranker, corpus, queries, sample,
                        ignore_identical_ids=ignore_identical_ids, **kwargs,
                    )
            except (OSError, TypeError, ValueError, KeyError, RuntimeError) as error:
                retriever.stop_multi_process_pool()
                if reranker is not None:
                    reranker.stop_multi_process_pool()
                raise ValueError(f"{self.eval_name} precheck failed for {dataset_options} ({split}): {error}") from error

        # Independent splits may use the same ID for different queries.
        all_queries = {qid: text for queries in queries_by_split.values() for qid, text in queries.items()}
        has_conflicting_ids = any(
            all_queries[qid] != text for queries in queries_by_split.values() for qid, text in queries.items()
        )
        query_batches = queries_by_split if has_conflicting_ids else {None: all_queries}
        search_results_by_batch = {
            batch: retriever(
                corpus=corpus,
                queries=queries,
                corpus_embd_save_dir=corpus_embd_save_dir,
                ignore_identical_ids=ignore_identical_ids,
                **kwargs,
            )
            for batch, queries in query_batches.items()
        }
        for split, path in result_paths.items():
            split_results = search_results_by_batch[split if has_conflicting_ids else None]
            rankings[split] = {qid: split_results[qid] for qid in queries_by_split[split]}
            self.save_search_results(
                eval_name=self.eval_name,
                model_name=str(retriever),
                reranker_name="NoReranker",
                search_results=rankings[split],
                output_path=path,
                split=split,
                **dataset_options,
            )
        return rankings, changed

    def _rerank_splits(
        self, splits, results_dir, save_name, retriever, reranker, rankings,
        ignore_identical_ids, dataset_options, *, rankings_changed=False, **kwargs,
    ):
        pending = {}
        for split in splits:
            path = results_dir / save_name.format(split=split)
            if self.overwrite or not path.exists():
                pending[split] = path
        if not pending:
            return False

        corpus = self.data_loader.load_corpus(**dataset_options)
        queries_by_split = {
            split: self.data_loader.load_queries(split=split, **dataset_options) for split in pending
        }
        if not rankings_changed:
            for split, queries in queries_by_split.items():
                try:
                    check_reranking_sample(
                        self, split, dataset_options, retriever, reranker, corpus, queries, rankings[split],
                        ignore_identical_ids=ignore_identical_ids, **kwargs,
                    )
                except (OSError, TypeError, ValueError, KeyError, RuntimeError) as error:
                    reranker.stop_multi_process_pool()
                    raise ValueError(f"{self.eval_name} reranking precheck failed for {dataset_options} ({split}): {error}") from error

        for split, path in pending.items():
            reranked = reranker(
                corpus=corpus,
                queries=queries_by_split[split],
                search_results=rankings[split],
                ignore_identical_ids=ignore_identical_ids,
                **kwargs,
            )
            self.save_search_results(
                eval_name=self.eval_name,
                model_name=str(retriever),
                reranker_name=str(reranker),
                search_results=reranked,
                output_path=path,
                split=split,
                **dataset_options,
            )
        return True

    def _write_metrics(self, rankings_dir, k_values, rankings_changed):
        metrics_path = rankings_dir / "EVAL" / "eval_results.json"
        if not rankings_changed and metrics_path.is_file():
            with metrics_path.open(encoding="utf-8") as file:
                cached_metrics = json.load(file)
            requested_cutoffs = set(map(str, k_values))
            if cached_metrics and all(
                {metric.rsplit("_at_", 1)[-1] for metric in scores} == requested_cutoffs
                for scores in cached_metrics.values()
            ):
                return

        metrics = self.evaluate_results(rankings_dir, k_values=k_values)
        self.output_eval_results_to_json(metrics, metrics_path)

    @staticmethod
    def save_search_results(
        eval_name: str,
        model_name: str,
        reranker_name: str,
        search_results: Dict[str, Dict[str, float]],
        output_path: str,
        split: str,
        dataset_name: Optional[str] = None,
    ):
        """Save the metadata and search results into a file.

        Args:
            eval_name (str): The experiment name of current evaluation.
            model_name (str): Name of model used.
            reranker_name (str): Name of reranker used.
            search_results (Dict[str, Dict[str, float]]): Dictionary of search results.
            output_path (str): Output path to write the results.
            split (str): Split used in searching.
            dataset_name (Optional[str], optional): Name of dataset used. Defaults to :data:`None`.
        """
        data = {
            "eval_name": eval_name,
            "model_name": model_name,
            "reranker_name": reranker_name,
            "split": split,
            "dataset_name": dataset_name,
            "search_results": search_results,
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_search_results(input_path: str):
        """Load search results from path.

        Args:
            input_path (str): Path to load from.

        Returns:
            dict, dict: data info that contains metadata and search results.
        """
        with open(input_path, "r", encoding="utf-8") as f:
            data_info = json.load(f)
        
        search_results = data_info.pop("search_results")
        return data_info, search_results

    @staticmethod
    def compute_metrics(
        qrels: Dict[str, Dict[str, int]],
        search_results: Dict[str, Dict[str, float]],
        k_values: List[int],
    ):
        """Evaluate the model with metrics.

        Args:
            qrels (Dict[str, Dict[str, int]]): Ground truth relevance of queries and documents.
            search_results (Dict[str, Dict[str, float]]): Dictionary of search results
            k_values (List[int]): Cutoffs.

        Returns:
            dict: The results of the metrics.
        """
        ndcg, _map, recall, precision = evaluate_metrics(
            qrels=qrels,
            results=search_results,
            k_values=k_values,
        )
        mrr = evaluate_mrr(
            qrels=qrels,
            results=search_results,
            k_values=k_values,
        )
        recall_cap = evaluate_recall_cap(
            qrels=qrels,
            results=search_results,
            k_values=k_values,
        )
        scores = {
            **{f"ndcg_at_{k.split('@')[1]}": v for (k, v) in ndcg.items()},
            **{f"map_at_{k.split('@')[1]}": v for (k, v) in _map.items()},
            **{f"recall_at_{k.split('@')[1]}": v for (k, v) in recall.items()},
            **{f"precision_at_{k.split('@')[1]}": v for (k, v) in precision.items()},
            **{f"mrr_at_{k.split('@')[1]}": v for (k, v) in mrr.items()},
            **{f"recall_cap_at_{k.split('@')[1]}": v for (k, v) in recall_cap.items()},
        }
        return scores

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

        for file in os.listdir(search_results_save_dir):
            if not file.endswith('.json'):
                continue

            file_path = os.path.join(search_results_save_dir, file)
            data_info, search_results = self.load_search_results(file_path)

            _eval_name = data_info['eval_name']
            assert _eval_name == self.eval_name, f'Mismatch eval_name: {_eval_name} vs {self.eval_name} in {file_path}'

            split = data_info['split']
            dataset_name = data_info.get('dataset_name', None)
            qrels = self.data_loader.load_qrels(dataset_name=dataset_name, split=split)

            eval_results = self.compute_metrics(
                qrels=qrels,
                search_results=search_results,
                k_values=k_values
            )

            if dataset_name is not None:
                key = f"{dataset_name}-{split}"
            else:
                key = split
            eval_results_dict[key] = eval_results

        return eval_results_dict

    @staticmethod
    def output_eval_results_to_json(eval_results_dict: dict, output_path: str):
        """Write the evaluation results into a json file.

        Args:
            eval_results_dict (dict): Dictionary of the evaluation results.
            output_path (str): Output path to write the json file.
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(eval_results_dict, f, indent=4)
        logger.info(f"Results saved to {output_path}")

    @staticmethod
    def get_results_df(metric: str, eval_results_dict: dict):
        """Get the results from dictionary to a DataFrame.

        Args:
            metric (str): Selected metric.
            eval_results_dict (dict): Dictionary of the evaluation results.

        Returns:
            DataFrame: DataFrame of the results.
        """
        results_dict = {}

        for model_name, model_results in eval_results_dict.items():
            results_dict[model_name] = {}
            for reranker_name, reranker_results in model_results.items():
                results_dict[model_name][reranker_name] = {}
                for split, split_results in reranker_results.items():
                    if metric in split_results:
                        results_dict[model_name][reranker_name][split] = split_results[metric]
                    else:
                        results_dict[model_name][reranker_name][split] = None

        model_reranker_pairs = []
        all_splits = set()
        for model_name, model_results in results_dict.items():
            for reranker_name, reranker_results in model_results.items():
                model_reranker_pairs.append((model_name, reranker_name))
                all_splits.update(reranker_results.keys())

        model_reranker_pairs.sort()
        multi_index = pd.MultiIndex.from_tuples(model_reranker_pairs, names=['Model', 'Reranker'])
        
        all_splits = sorted(list(all_splits))
        overall_columns = ['average'] + all_splits
        overall_df = pd.DataFrame(index=multi_index, columns=overall_columns)
        
        for model, reranker in model_reranker_pairs:
            for split in all_splits:
                if model in results_dict and reranker in results_dict[model] and split in results_dict[model][reranker]:
                    overall_df.loc[(model, reranker), split] = results_dict[model][reranker][split]
                else:
                    overall_df.loc[(model, reranker), split] = None
            if overall_df.loc[(model, reranker), all_splits].isnull().any():
                overall_df.loc[(model, reranker), 'average'] = None
            else:
                overall_df.loc[(model, reranker), 'average'] = overall_df.loc[(model, reranker), all_splits].mean()

        return overall_df

    @staticmethod
    def output_eval_results_to_markdown(eval_results_dict: dict, output_path: str, metrics: Union[List[str], str]):
        """Write the evaluation results to a markdown file.

        Args:
            eval_results_dict (dict): Dictionary that contains evaluation results.
            output_path (str): Path to write the output to.
            metrics (Union[List[str], str]): The metrics that will be written in the markdown file.
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if isinstance(metrics, str):
            metrics = [metrics]

        with open(output_path, 'w', encoding='utf-8') as f:
            for metric in metrics:
                f.write(f"## {metric}\n\n")
                results_df = AbsEvaluator.get_results_df(metric, eval_results_dict)
                max_index = results_df.dropna(axis=1, how="all").idxmax(axis=0).to_dict()
                splits = results_df.columns
                f.write(f"| Model | Reranker | {' | '.join(splits)} |\n")
                f.write(f"| :---- | :---- | {' | '.join([':---:' for _ in splits])} |\n")
                for i, row in results_df.iterrows():
                    line = f"| {i[0]} | {i[1]} | "
                    for s, v in row.items():
                        if pd.isna(v):
                            line += "- | "
                        else:
                            if i != max_index.get(s):
                                line += f'{v*100:.3f} | '
                            else:
                                line += f'**{v*100:.3f}** | '
                    f.write(line + "\n")
                f.write("\n")
        logger.info(f"Results saved to {output_path}")
