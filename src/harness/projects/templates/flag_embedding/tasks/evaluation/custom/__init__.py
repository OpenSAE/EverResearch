from dataclasses import dataclass, field

from FlagEmbedding.abc.evaluation import (
    AbsEvalArgs,
    AbsEvalModelArgs as CustomEvalModelArgs,
)

from .data_loader import CustomEvalDataLoader
from .runner import CustomEvalRunner


@dataclass
class CustomEvalArgs(AbsEvalArgs):
    precheck_only: bool = field(default=False, metadata={"help": "Check a local retrieval sample and exit."})


__all__ = [
    "CustomEvalArgs",
    "CustomEvalModelArgs",
    "CustomEvalRunner",
    "CustomEvalDataLoader",
]
