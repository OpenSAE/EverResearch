# Inputs and datasets

## Purpose and features

Identify the input media and annotation formats accepted by SAM 2 prediction, training and evaluation.

## Scope

Use this page to select example inputs or supply a local dataset to the corresponding command.

## Notebook examples and other images

Image prediction takes an RGB image and pixel prompts. The notebook example images include `data/notebook_images/upstream/truck.jpg`, whose demo prompt is a foreground click near `(500, 375)`. The image command takes an explicit image path and a dataset name such as `notebook_images` to record the source.

The video notebook reads numbered JPEGs in `data/notebook_videos/upstream/bedroom/`. The public video predictor accepts such a directory or an MP4 file. Its JPEG loader sorts by the integer filename stem. The demo gallery's own MP4 inputs live in `third_party/meta_web_demo/data/gallery/`.

## SA-V, DAVIS-style datasets, and MOSE

- SA-V train uses video files with automatic and manual masklet JSON. The training example extracts JPEG frames and loads the JSON masklets through the dataset classes. The repository includes an example video and annotations under `data/annotated_video/upstream/`. [SA-V dataset guide](code/dataset.md)
- SA-V validation and test use individual binary PNG files under `video/object/frame.png`. Pass `--per_obj_png_file` to preserve that structure during inference. Evaluation selects frames from the ground truth and by default drops the first and last annotated frame for each object. [VOS command](code/video.md)
- DAVIS-style datasets use one indexed annotation PNG per frame that stores all object IDs. The MOSE fine-tuning recipe takes explicit `dataset.img_folder` and `dataset.gt_folder` paths. It selects training clips through the supplied sample training list. The separately supplied sample validation list is used with VOS prediction and evaluation. [Training guide](code/training.md)
- SA-1B is an example of an image dataset in the training guide. Training datasets use loaders and samplers in `datasets/video_objects/` to produce frame and object batches for the trainer. [Mixed image and video training](code/training.md#training-on-images-and-videos)
