# Training configuration

## Purpose and main function

The training launcher composes Hydra recipes and passes their resolved settings to the dataset loader, VGGT model, optimizer, and trainer.

## Scope

Use this page to inspect the supplied fine-tuning recipe or prepare a separate recipe in its own directory. Use the [training guide](code/training.md) for data preparation and launch commands.

Run `python main.py train --print-config` to print the effective default recipe without starting the trainer or creating an output directory. To inspect another recipe, pass `--config /absolute/path/to/recipe.yaml`. A recipe can compose the shared data settings before applying its own values. Keep `${...}` references when related settings should follow one value. The run manifest points to the configuration saved for that execution.

## `conf/`

### `config.yaml`

The default recipe fine-tunes the camera and depth heads on Co3D. It applies its own values after composing the shared dataset settings. [Recipe source](../conf/config.yaml)

| Setting | Default and effect |
| --- | --- |
| `mode` | The launcher runs training with validation when omitted. Set `val` to run validation only from `data.val`. |
| `data.train.dataset.dataset_configs`, `data.val.dataset.dataset_configs` | Train and validation use `Co3dDataset` with `split: train` and `split: test` respectively. Replace the `CO3D_DIR` and `CO3D_ANNOTATION_DIR` placeholders in both entries. Additional dataset entries can be composed with the same loader. |
| `img_size`, `patch_size`, `max_img_per_gpu`, `num_workers` | The loader prepares images using a reference size of `518` pixels and a patch size of `14`. It uses an image budget of `48` per GPU and `8` worker processes. |
| `seed_value`, `accum_steps`, `max_epochs` | The trainer uses seed `42`, divides a batch into `2` gradient accumulation chunks, and runs for up to `20` epochs. |
| `limit_train_batches`, `limit_val_batches`, `val_epoch_freq` | The train and validation loops stop after their inclusive zero-based batch index limits of `800` and `400`. The trainer schedules intermediate validation at epoch indices divisible by `5`, and validates again after training. |
| `model.enable_camera`, `model.enable_depth`, `model.enable_point`, `model.enable_track` | Camera and depth are enabled. Point-map and tracking are disabled. Pair any enabled supervised head with a corresponding loss and the labels it consumes. |
| `loss.camera`, `loss.depth`, `loss.point`, `loss.track` | The recipe uses a camera loss with L1 and weight `5`, and a depth loss with gradient supervision and weight `1`. Point and tracking losses are disabled in this recipe. |
| `optim.optimizer`, `optim.options` | AdamW uses recipe values of `5e-5` for learning rate and `0.05` for weight decay. Training schedules the learning rate from `1e-8` through `5e-5` and back to `1e-8`, and retains weight decay at `0.05`. |
| `optim.frozen_module_names`, `optim.gradient_clip`, `optim.amp` | The recipe freezes the aggregator, configures a norm limit of `1` for the listed modules, and enables bfloat16 mixed precision. |
| `exp_name`, `experiment_dir` | The default purpose is `camera_depth`. With the `experiment_dir` key present, the launcher derives the experiment path from the data, model, mode, and purpose. `--run-name` overrides the purpose. Use one to three lowercase words joined by underscores, such as `depth_comparison`. |
| `logging.log_dir`, `logging.tensorboard_writer.path`, `logging.log_freq` | The default managed paths store each execution's logs under its own directory and TensorBoard output in its `tensorboard/` subdirectory. Metrics are logged every iteration. |
| `checkpoint.save_dir`, `checkpoint.save_freq`, `checkpoint.resume_checkpoint_path`, `checkpoint.strict` | The default managed path stores each attempt's checkpoints separately. A rolling checkpoint is saved each epoch and a numbered checkpoint every five epochs after epoch zero. Supply an initial local checkpoint or set the resume path to `null` to search existing managed runs. Model state loading uses `strict: false` by default. |
| `distributed`, `cuda` | The default recipe uses the NCCL distributed backend with a 30-minute initialization timeout. It allows TF32 and disables cuDNN benchmarking and deterministic mode. |

`--legacy-output` restores `logs/` and `logs/exp001/ckpts/`, or uses the purpose supplied with `--run-name`. Existing recipes without `experiment_dir` retain their explicit log and checkpoint paths.

### `tasks/fine_tune/dataset.yaml`

This file supplies shared loader and augmentation settings for both `data.train` and `data.val`. The default recipe overrides the image size, worker count, and image budget where it declares those values. [Shared settings source](../conf/tasks/fine_tune/dataset.yaml)

| Setting under each split | Default and effect |
| --- | --- |
| `_target_`, `shuffle`, `pin_memory` | `DynamicTorchDataset` prepares distributed batches. Shuffling is enabled and page-locked loader buffers are disabled. |
| `common_config.fix_img_num`, `common_config.img_nums`, `common_config.fix_aspect_ratio` | Frame count is sampled because `fix_img_num` is `-1`. The ranges are 2–24 frames for training and 2–12 for validation. The fixed aspect ratio is `1.0` when the loader uses a fixed frame count. |
| `common_config.training`, `common_config.load_depth`, `common_config.load_track`, `common_config.track_num` | The loader distinguishes training from validation, loads depth for both, and keeps track labels disabled. Its configured track count is `1024` when tracking labels are enabled. |
| `common_config.inside_random`, `common_config.get_nearby`, `common_config.allow_duplicate_img` | The recipe enables reader-level random selection, nearby frame selection where supported, and repeat sampling of frames. |
| `common_config.rescale`, `common_config.rescale_aug`, `common_config.augs` | Both splits use image scaling. Training can perturb the scale and aspect ratio, apply correlated color jitter, and convert images to grayscale. Validation uses a fixed square aspect range, disables color and grayscale augmentation, and leaves geometric scale augmentation disabled. |
| `common_config.debug`, `common_config.repeat_batch`, `common_config.landscape_check` | Debug-mode data selection, repeating training batches, and checking orientation for a landscape target are disabled in the supplied recipe. |
