from ..cogvideox_text.lora_trainer import CogVideoXT2VLoraTrainer
from ..registry import register


class CogVideoXT2VSftTrainer(CogVideoXT2VLoraTrainer):
    pass


register("cogvideox-t2v", "sft", CogVideoXT2VSftTrainer)
