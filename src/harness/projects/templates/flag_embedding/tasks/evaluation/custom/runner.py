import logging
from pathlib import Path

from FlagEmbedding.abc.evaluation import AbsEvalRunner
from FlagEmbedding.precheck.retrieval import check_retrieval

from .data_loader import CustomEvalDataLoader

logger = logging.getLogger(__name__)


class CustomEvalRunner(AbsEvalRunner):
    data_loader_class = CustomEvalDataLoader

    def _dataset_names(self, loader):
        if self.eval_args.dataset_names is None:
            return loader.available_dataset_names() or [None]
        return loader.check_dataset_names(self.eval_args.dataset_names)

    def load_data_loader(self) -> CustomEvalDataLoader:
        loader = super().load_data_loader()
        if not any(loader.check_splits(self.eval_args.splits, dataset_name=name) for name in self._dataset_names(loader)):
            raise ValueError(f"No query and relevance file pair found for the requested splits: {self.eval_args.splits}")
        return loader

    def run(self):
        args = self.eval_args
        precheck_only = getattr(args, "precheck_only", False)
        output = Path(args.output_dir) / str(self.retriever)
        stages = ["NoReranker"]
        if self.reranker is not None:
            stages.append(str(self.reranker))
        for name in self._dataset_names(self.data_loader):
            dataset_dir = Path(args.dataset_dir) / name if name else Path(args.dataset_dir)
            splits = self.data_loader.check_splits(args.splits, dataset_name=name)
            filenames = [f"{name}-{split}.json" if name else f"{split}.json" for split in splits]
            needs_rankings = any(not (output / stage / filename).is_file() for stage in stages for filename in filenames)
            if precheck_only or args.overwrite or needs_rankings:
                for split in splits:
                    check_retrieval(
                        self.evaluator, dataset_dir, name, split, self.retriever, self.reranker, args.ignore_identical_ids,
                        files_only=not precheck_only,
                    )
                    if precheck_only:
                        logger.info("Local retrieval precheck passed for %s (%s)", dataset_dir, split)

        if precheck_only:
            self.retriever.stop_multi_process_pool()
            if self.reranker is not None:
                self.reranker.stop_multi_process_pool()
            return
        return super().run()
