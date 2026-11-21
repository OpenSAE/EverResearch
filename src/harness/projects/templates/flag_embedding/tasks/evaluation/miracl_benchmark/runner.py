from FlagEmbedding.abc.evaluation import AbsEvalRunner

from .data_loader import MIRACLEvalDataLoader


class MIRACLEvalRunner(AbsEvalRunner):
    """
    Evaluation runner of MIRACL.
    """
    data_loader_class = MIRACLEvalDataLoader
