import json
import logging
import os
from pathlib import Path
from typing import Tuple, Union

import mteb

from FlagEmbedding.abc.evaluation import AbsEvalRunner, AbsEvalModelArgs

from .arguments import MTEBEvalArgs
from .prompts import get_task_def_by_task_name_and_type
from .searcher import MTEBEvalDenseRetriever, MTEBEvalReranker


logger = logging.getLogger(__name__)


class MTEBEvalRunner(AbsEvalRunner):
    """
    Evaluation runner of MTEB.
    """
    def __init__(
        self,
        eval_args: MTEBEvalArgs,
        model_args: AbsEvalModelArgs,
    ):
        self.eval_args = eval_args
        self.model_args = model_args

        self.retriever, self.reranker = self.load_retriever_and_reranker()

    def load_retriever_and_reranker(self) -> Tuple[MTEBEvalDenseRetriever, Union[MTEBEvalReranker, None]]:
        """Load the retriever and reranker

        Returns:
            Tuple[MTEBEvalDenseRetriever, Union[MTEBEvalReranker, None]]: The retriever and reranker instances.
        """
        embedder, reranker = self.get_models(self.model_args)
        retriever = MTEBEvalDenseRetriever(
            embedder,
            search_top_k=self.eval_args.search_top_k,
            overwrite=self.eval_args.overwrite
        )
        if reranker is not None:
            reranker = MTEBEvalReranker(reranker, rerank_top_k=self.eval_args.rerank_top_k)
        return retriever, reranker

    def read_results(self, output_folder, tasks):
        """Read the evaluation results from directory.

        Args:
            output_folder (str): Path to the directory with results.
            tasks (list): List of MTEB tasks.

        Returns:
            dict: The results of all the tasks.
        """
        tasks_results = {}
        task_types = list(set([t.metadata.type for t in tasks]))
        for t_type in task_types:
            tasks_results[t_type] = {}
            for t in tasks:
                if t.metadata.type != t_type: continue
                task_name = t.metadata.name

                metric = t.metadata.main_score
                split = t.metadata.eval_splits[0]

                if os.path.exists(os.path.join(output_folder, task_name + '.json')):
                    data = json.load(open(os.path.join(output_folder, task_name + '.json')))
                    tasks_results[t_type][task_name] = {}
                    for s in ['test', 'dev', 'validation']:
                        if s in data['scores']:
                            split = s
                            break
                        split = None
                    if split is None:
                        print('ERROR')
                        break

                    temp_datas = data['scores'][split]
                    temp_data = None
                    for td in temp_datas:
                        if td['hf_subset'] == 'default':
                            temp_data = td
                    if temp_data is None:
                        temp_data = temp_datas[0]
                    tasks_results[t_type][task_name] = round(temp_data['main_score'] * 100, 2)

        print(f"tasks_results: {tasks_results}")
        return tasks_results

    def output_json(self, tasks_results, save_file):
        """Save the tasks results into a json file.

        Args:
            tasks_results (dict): The task results.
            save_file (str): Path to a file to save the results.
        """
        all_results = 0
        all_results_num = 0
        cqa_results = 0
        cqa_results_num = 0

        new_results = {}
        for task_type in tasks_results.keys():
            new_results[task_type] = {}
            tmp_results = 0
            tmp_results_num = 0
            for task_name in tasks_results[task_type].keys():
                if "CQADupstack" in task_name:
                    cqa_results += tasks_results[task_type][task_name]
                    cqa_results_num += 1
                else:
                    new_results[task_type][task_name] = float(round(tasks_results[task_type][task_name], 2))
                    all_results_num += 1
                    all_results += tasks_results[task_type][task_name]
                    tmp_results_num += 1
                    tmp_results += tasks_results[task_type][task_name]
            if cqa_results_num > 0:
                cqa_results = cqa_results / cqa_results_num
                new_results[task_type]["CQADupstack"] = float(round(cqa_results, 2))
                all_results += cqa_results
                all_results_num += 1
                tmp_results += cqa_results
                tmp_results_num += 1
            new_results[task_type]['Avg'] = float(round(tmp_results / tmp_results_num, 2))
        new_results['Avg'] = float(round(all_results / all_results_num, 2))
        with open(save_file, 'w') as f:
            json.dump(new_results, f)

    def run(self):
        """
        Run the evaluation.
        """
        task_types = self.eval_args.task_types
        tasks = self.eval_args.tasks
        languages = self.eval_args.languages
        tasks = mteb.get_tasks(
            languages=languages,
            tasks=tasks,
            task_types=task_types
        )
        output_folder = Path(self.eval_args.output_dir) / str(self.retriever)
        default_instruction = self.retriever.get_instruction()
        examples_path = self.eval_args.examples_path
        if examples_path is not None and not callable(getattr(self.retriever.embedder, "set_examples", None)):
            logger.warning("The selected embedder does not support --examples_path")
            examples_path = None

        for task in tasks:
            task_name = task.metadata.name
            task_type = task.metadata.type

            self.retriever.stop_pool()

            if self.eval_args.use_special_instructions:
                try:
                    instruction = get_task_def_by_task_name_and_type(task_name, task_type)
                except (KeyError, ValueError):
                    logger.info(f"No instruction found for {task_name}")
                    instruction = default_instruction
                self.retriever.set_instruction(instruction)

            if examples_path is not None:
                task_file = Path(examples_path) / f"{task_name}.json"
                try:
                    with task_file.open(encoding="utf-8") as file:
                        examples = json.load(file)
                except FileNotFoundError:
                    logger.info(f"No examples found for {task_name}")
                    examples = None
                self.retriever.set_examples(examples)

            if task_type == 'Classification':
                self.retriever.set_normalize_embeddings(False)
            else:
                self.retriever.set_normalize_embeddings(True)

            evaluation = mteb.MTEB(tasks=[task])
            evaluation.run(
                self.retriever,
                output_folder=str(output_folder),
                overwrite_results=self.eval_args.overwrite,
            )

        Path(self.eval_args.eval_output_path).parent.mkdir(parents=True, exist_ok=True)
        logger.info("Start computing metrics. Only save results as json.")
        tasks_results = self.read_results(output_folder / "no_model_name_available" / "no_revision_available", tasks)
        self.output_json(tasks_results, self.eval_args.eval_output_path)
