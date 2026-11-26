from ..cogvideox_image.lora_trainer import CogVideoXI2VLoraTrainer
from ..registry import register


class CogVideoXI2VSftTrainer(CogVideoXI2VLoraTrainer):
    pass


register("cogvideox-i2v", "sft", CogVideoXI2VSftTrainer)
