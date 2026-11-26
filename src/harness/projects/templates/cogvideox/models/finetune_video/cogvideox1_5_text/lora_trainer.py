from ..cogvideox_text.lora_trainer import CogVideoXT2VLoraTrainer
from ..registry import register


class CogVideoX1_5T2VLoraTrainer(CogVideoXT2VLoraTrainer):
    pass


register("cogvideox1.5-t2v", "lora", CogVideoX1_5T2VLoraTrainer)
