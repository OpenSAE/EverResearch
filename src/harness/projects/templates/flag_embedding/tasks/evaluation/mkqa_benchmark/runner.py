from FlagEmbedding.abc.evaluation import AbsEvalRunner

from .data_loader import MKQAEvalDataLoader
from .evaluator import MKQAEvaluator


class MKQAEvalRunner(AbsEvalRunner):
    """
    Evaluation runner of MKQA.
    """
    data_loader_class = MKQAEvalDataLoader

    def load_evaluator(self) -> MKQAEvaluator:
        """Load the evaluator instance by args.

        Returns:
            MKQAEvaluator: The MKQA evaluator instance.
        """
        evaluator = MKQAEvaluator(
            eval_name=self.eval_args.eval_name,
            data_loader=self.data_loader,
            overwrite=self.eval_args.overwrite,
        )
        return evaluator
