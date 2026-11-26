# Research tasks

## Purpose and features

Find a command or Python interface for SAM 2 image prediction, video tracking, evaluation and fine-tuning.

## Scope

Run the commands from the repository root after installing the dependencies for the selected task.

## Point-prompt image prediction

```bash
python main.py image --print-config \
  --dataset notebook_images --image assets/examples/notebook_images/files/truck.jpg --point 500 375 1

python main.py image \
  --dataset notebook_images --image assets/examples/notebook_images/files/truck.jpg --point 500 375 1
```

The command uses the SAM 2.1 Hiera Large configuration and its local checkpoint at `../data/sam2/checkpoints/local/sam2.1_hiera_large.pt` by default. See the released model table for available weights. Prompts are pixel coordinates measured from the upper-left of the image. Repeat `--point X Y LABEL` for additional foreground (`1`) or background (`0`) points.

Prediction prints the path to the saved `.npz`. Pass it to `python main.py image --read-result PATH` for its settings, scores and shapes. The [experiment guide](experiment.md) describes the saved arrays. To use boxes, refine prompts with previous logits or predict on a batch of images, see the [Python image predictor notebook](../scripts/examples/image_predictor_example.ipynb).

## Automatic image masks

`SAM2AutomaticMaskGenerator` collects and filters masks from sampled point prompts. The notebook shows how to configure the sampling grid and use the returned masks. [Automatic masks notebook](../scripts/examples/automatic_mask_generator_example.ipynb)

## Video tracking and evaluation

The Python video predictor accepts box, point or mask prompts and propagates the resulting objects through the video. [Video predictor notebook](../scripts/examples/video_predictor_example.ipynb)

Use `python main.py video` for batch tracking from annotation PNGs. The VOS command writes PNGs using the matching format. Use `python main.py evaluate --gt_root ... --pred_root ...` to match predictions against annotated frames. The evaluator reports region overlap (J) and boundary accuracy (F), with their mean J&F, in `results.csv` under the prediction root. [Video inference options](code/video.md) · [Evaluation protocol](code/dataset.md#sa-v-val-and-test-evaluation)

## Training and fine-tuning

`python main.py train -c configs/sam2.1_training/sam2.1_hiera_b+_MOSE_finetune.yaml` composes the MOSE recipe, connects training samples to the training model and queues a local or Slurm job. Configure dataset roots and a Base Plus checkpoint before launching. Add `--print-config` to review resolved settings. Training produces checkpoints, logs and TensorBoard events for the selected experiment. [Training commands and requirements](code/training.md)
