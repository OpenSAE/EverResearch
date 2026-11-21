from dataclasses import dataclass, field
from typing import List

from FlagEmbedding.abc.evaluation.arguments import AbsEvalArgs


@dataclass
class MTEBEvalArgs(AbsEvalArgs):
    """
    Argument class for MTEB evaluation.
    """
    languages: List[str] = field(
        default=None, metadata={"help": "Languages to evaluate. The default applies no language filter."}
    )
    tasks: List[str] = field(
        default=None, metadata={"help": "Tasks to evaluate. Default: None"}
    )
    task_types: List[str] = field(
        default=None, metadata={"help": "The task types to evaluate. Default: None"}
    )
    use_special_instructions: bool = field(
        default=False, metadata={"help": "Whether to use specific instructions in `prompts.py` for evaluation. Default: False"}
    )
    examples_path: str = field(
        default=None,
        metadata={"help": "Directory of <task_name>.json files with few-shot examples for an ICL embedder."},
    )
