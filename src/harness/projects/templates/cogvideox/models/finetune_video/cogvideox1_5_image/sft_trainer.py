from ..cogvideox_image.sft_trainer import CogVideoXI2VSftTrainer
from ..registry import register


class CogVideoX1_5I2VSftTrainer(CogVideoXI2VSftTrainer):
    pass


register("cogvideox1.5-i2v", "sft", CogVideoX1_5I2VSftTrainer)
