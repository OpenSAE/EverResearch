from ..cogvideox_text.sft_trainer import CogVideoXT2VSftTrainer
from ..registry import register


class CogVideoX1_5T2VSftTrainer(CogVideoXT2VSftTrainer):
    pass


register("cogvideox1.5-t2v", "sft", CogVideoX1_5T2VSftTrainer)
