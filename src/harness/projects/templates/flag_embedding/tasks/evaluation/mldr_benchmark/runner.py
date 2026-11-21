from FlagEmbedding.abc.evaluation import AbsEvalRunner

from .data_loader import MLDREvalDataLoader


class MLDREvalRunner(AbsEvalRunner):
    """
    Evaluation runner of MLDR.
    """
    data_loader_class = MLDREvalDataLoader
