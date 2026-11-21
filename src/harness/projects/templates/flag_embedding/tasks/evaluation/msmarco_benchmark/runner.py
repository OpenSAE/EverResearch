from FlagEmbedding.abc.evaluation import AbsEvalRunner

from .data_loader import MSMARCOEvalDataLoader


class MSMARCOEvalRunner(AbsEvalRunner):
    """
    Evaluation runner of MSMARCO.
    """
    data_loader_class = MSMARCOEvalDataLoader
