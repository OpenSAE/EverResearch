# Configuration and recipes

[`conf/config.yaml`](../conf/config.yaml) supplies the default image model, device and study purpose and registers the available configuration files. Pass `--model`, `--device`, `--name` or `--checkpoint` on the image command to override defaults. Use `--print-config` to see the fully resolved settings before loading a checkpoint.

## SAM 2 model recipes

[`conf/models/segment_anything/config.yaml`](../conf/models/segment_anything/config.yaml) contains the original Hydra recipes under their published keys.

| Version | Hiera recipes |
| --- | --- |
| SAM 2 | `configs/sam2/sam2_hiera_t.yaml`, `configs/sam2/sam2_hiera_s.yaml`, `configs/sam2/sam2_hiera_b+.yaml`, `configs/sam2/sam2_hiera_l.yaml` |
| SAM 2.1 | `configs/sam2.1/sam2.1_hiera_t.yaml`, `configs/sam2.1/sam2.1_hiera_s.yaml`, `configs/sam2.1/sam2.1_hiera_b+.yaml`, `configs/sam2.1/sam2.1_hiera_l.yaml` |

## MOSE fine-tuning recipe

[`conf/tasks/fine_tuning/config.yaml`](../conf/tasks/fine_tuning/config.yaml) defines `configs/sam2.1_training/sam2.1_hiera_b+_MOSE_finetune.yaml`. Set `dataset.img_folder` and `dataset.gt_folder` before launching. Select `--experiment-log-dir` to retain an existing output location or override the default. Launch settings passed on the command line take precedence over the recipe. [Training instructions](code/training.md)
