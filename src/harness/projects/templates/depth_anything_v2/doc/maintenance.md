# EverResearch adoption and verification

## Purpose and main function

Record the source migration and the checks completed on the adopted Depth Anything V2 project.

## Scope of application

Use this page to trace the original workflows to their current implementations and interpret the saved verification runs.

Source: [DepthAnything/Depth-Anything-V2@a561b849eb](https://github.com/DepthAnything/Depth-Anything-V2/tree/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf). The template carries the migrated source, portable split lists, and the upstream example media under [assets](../assets).

| Original workflow | Current entry and source |
| --- | --- |
| `run.py` and `metric_depth/run.py` | `depth-anything image` and `depth-anything metric` call [image prediction](../tasks/image_depth/predict.py), using the relative or metric head from [the model package](../models/depth_anything_v2). |
| `run_video.py` | `depth-anything video` calls [frame inference](../tasks/video_depth/predict.py). |
| `metric_depth/depth_to_pointcloud.py` | `depth-anything pointcloud` calls the [colored PLY exporter](../tasks/point_cloud/export.py). |
| `app.py` | `depth-anything demo` serves the [interactive Gradio interface](../tasks/demo/interface.py). |
| `metric_depth/train.py` and `dist_train.sh` | [The distributed launcher](../scripts/distributed_training.sh) calls [training and evaluation](../tasks/training/train.py). |
| `metric_depth/dataset/` | Hypersim, Virtual KITTI 2, and KITTI each have a [dataset reader](../datasets). The original split lists are under [assets/splits](../assets/splits). |

The wheel packages the relative model under its existing public import `depth_anything_v2.dpt.DepthAnythingV2`. Metric callers use `depth_anything_v2.metric.MetricDepthAnythingV2`. The model families share the existing backbone and decoder layers, with the upstream metric sigmoid head and meter scaling preserved.

## Verification

- The original and installed image commands processed the same bundled image using the local Small weights at input size 518. The relative preview, metric preview, and metric array matched their original outputs element by element.
- The installed commands ran from outside the workspace and produced a readable two-frame MP4 and colored PLY with 272,000 points.
- The local demo processed an 84 × 56 image and returned the comparison slider, an 8-bit grayscale PNG, and a 16-bit depth PNG.
- One GPU completed an epoch with a tiny synthetic input. The checkpoint and TensorBoard log both opened and contained training and validation state.
- The installed precheck resolved the EverResearch weight binding and rejected a missing checkpoint before creating a run. Strict layout, dependency, and experiment checks passed, including five retained runs.

## Whole-project acceptance

The online project launcher and the EverResearch strict structure check passed with zero violations. The installed command ran from outside the project and its Python environment passed the dependency check. The fresh workflow runs used Python 3.12.15, PyTorch 2.10.0 with CUDA 12.8, and one NVIDIA GeForce RTX 5090.

| Workflow | Fresh evidence |
| --- | --- |
| Relative image depth | Single-image run used the Small relative checkpoint at input size 518 and produced a readable RGB preview. |
| Metric image depth | Single-image run used the Small indoor checkpoint at input size 518. The saved 1,362 × 2,048 array contained finite depths from 2.828 to 19.780 meters. |
| Video depth | Bundled basketball run used the Small relative checkpoint at input size 518. A fresh run with the automatic check produced 89 matching decoded frames. The two-frame acceptance run also passed. |
| Point clouds | Single-image run used the Small indoor checkpoint and exported 2,789,376 colored points. |
| Gradio demo | The installed command started a local server. An actual 84 × 56 image request returned the comparison slider and readable 8-bit and 16-bit PNGs in 3.5 seconds including startup. |
| Hypersim training | Official-sample run used one original training pair and one original validation pair. One batch completed a backward pass and optimizer step. The checkpoint and ten finite TensorBoard scalars reopened successfully. |
| Virtual KITTI 2 training and KITTI validation | Official-sample run used one original pair from each retained split. One batch completed a backward pass and optimizer step. The checkpoint and ten finite TensorBoard scalars reopened successfully. |

The official sample lists name the archive members and retained split rows. The dataset readers decoded aligned image and depth pairs, produced float32 depths in meters, and generated valid-pixel masks. Single-file, directory, and text-list input selections were exercised through the public media interface.

The nine published checkpoints passed strict weight loading in the installed model factory. Each processed a real 84 × 56 sample at input size 56 and returned a finite float32 array at the source resolution. The metric outputs stayed within the configured 20-meter indoor and 80-meter outdoor maxima. The downloaded checkpoint digests matched those advertised by the publisher. See the [relative checkpoint list](../README.md#pre-trained-models) and [metric checkpoint list](models.md#pre-trained-models).

The Giant relative and metric architectures both ran a forward pass with random initialization. Pretrained Giant acceptance awaits a published matching checkpoint. The [upstream release table](https://github.com/DepthAnything/Depth-Anything-V2#pre-trained-models) lists Giant as upcoming.

## Automatic precheck acceptance

The installed image, metric, video, point cloud, demo, and training commands now run bounded checks through their production loaders, model and output code. The standalone `--precheck` mode reports its actual compute and readback without starting a formal run. The video check reads and writes one frame. Training uses isolated model and optimizer state for one backward pass and optimizer step, then reopens validation and loss metrics from TensorBoard. Python, NumPy, and PyTorch random states are restored before formal training. The demo checks a bundled image before it opens the server.

| Workflow | Successful formal launch | Rejected formal launch |
| --- | --- | --- |
| Relative image depth | Verified precheck and prediction | Unreadable image |
| Metric image depth | Verified precheck and prediction | Unreadable image |
| Video depth | Verified precheck and prediction | Unreadable video |
| Point clouds | Verified precheck and export | Unreadable image |
| Hypersim training | Verified precheck and training | Depth limit incompatible with the training sample |
| Virtual KITTI 2 training and KITTI validation | Verified precheck and training | Depth limit incompatible with the training sample |
| DA-2K pairwise depth | Verified precheck and scoring | Missing checkpoint |

The paired EverResearch checker verifies the automatic gate from each successful and rejected record. The successful records include timing and sample counts. The rejected records preserve the cause and show that formal execution did not start. The demo was checked through its standalone precheck, an actual loopback inference request and a launch that rejected a missing checkpoint before it opened the server.

## Formal run choices

Reference timings were measured during adoption. Reproduce them with the data, weights, and commands below; run artifacts belong to your copied project.
The estimates use the new short profiles on one NVIDIA GeForce RTX 5090 with 32 GB of memory, Python 3.12.15, PyTorch 2.10.0 with CUDA 12.8, and local input and output storage. Each profile had a five-minute limit for process startup, precheck, computation, and output writes. The timed workloads used the GPU serially. Queue time and input preparation stayed outside the timer. The profiles reused local publisher data and weights.

| Formal run | Dataset, checkpoint, and complete workload | Observed sample and startup | Estimated wall time |
| --- | --- | --- | --- |
| Relative depth previews | All **1,033 DA-2K images**, Large relative weights, one pass, one image at a time, inference size 518. Writes 1,033 PNGs, about 4.5 GB. | 10 real images in **8.6 s**. Startup and precheck 6.3 s, then 2.3 s through PNG output and exit.  | **3–5 min** |
| Indoor metric depth | All **195 DA-2K indoor images**, Large Hypersim metric weights, one pass, one image at a time, inference size 518, 20 m maximum. Writes 195 PNGs and 195 metric arrays, about 3 GB. | 10 real images in **8.0 s**. Startup and precheck 5.5 s, then 2.5 s through output and exit.  | **40–70 s** |
| Video depth | Bundled basketball clip, all **89 consecutive frames**, Small relative weights, one pass, inference size 518. Writes one MP4, about 49 MB. | 10 consecutive frames in **6.3 s**. Startup and precheck 2.6 s, then 3.7 s through video output and exit.  | **28–50 s** |
| Colored point clouds | **100 Hypersim validation RGB images** from four official scenes, Small Hypersim metric weights, one pass at native-image-height input, 20 m maximum. Writes 100 PLY files, 2.1 GB. | 10 native images in **4.4 s**. Startup and precheck 2.7 s, then 1.6 s through PLY output and exit.  | **12–21 s** |
| Interactive demo | All **1,033 DA-2K images**, Large relative weights, one independent loopback upload per image, inference size 518. Returns one comparison and two PNG downloads per request. | 10 independent requests in **12.0 s**. Service ready after 6.3 s. Average 0.53 s per request, including reopening both downloads.  | **7–13 min** |
| DA-2K pairwise benchmark | All **1,033 images and 2,068 annotated pairs** across eight official scenarios, Large relative weights, one prediction per image at size 518. Writes per-scenario closer-point accuracy and its unweighted mean to JSON. | 10 images and 21 pairs in **6.9 s**. Model and precheck 4.3 s, scoring 1.0 s.  | **80–150 s** |
| Hypersim fine-tuning | **59,543 train and 7,386 validation pairs**, Large relative backbone initialization with metric head, 120 epochs, 518-pixel inputs, batch 4 per GPU, four loader workers per rank, 20 m maximum. Runs validation and overwrites its checkpoint each epoch. | Three batches of four and 10 validation pairs in **23.9 s**. First batch complete at 18.6 s. Next batches averaged 0.444 s, then validation took 1.2 s and checkpoint plus exit took 3.2 s.  | **8–14 days** on one RTX 5090 |
| Virtual KITTI 2 fine-tuning with KITTI validation | **19,559 train and 652 validation pairs**, Large relative backbone initialization with metric head, 120 epochs, 518-pixel inputs, batch 4 per GPU, four loader workers per rank, 80 m maximum. Runs validation and overwrites its checkpoint each epoch. | Three batches of four and 10 validation pairs in **26.1 s**. First batch complete at 19.5 s. Next batches averaged 0.444 s, then validation took 2.7 s and checkpoint plus exit took 3.1 s.  | **2.6–4.3 days** on one RTX 5090 |

The DA-2K preview, demo, and score samples cover all eight scenarios. With one or two images per scenario, the ranges allow for file size and latency variation throughout the full set. The first nine item-to-item spans averaged 0.197 s for relative preview output, 0.212 s for metric output, and 0.117 s for PLY export. The last measured span also includes finalization and process exit. Video scales the ten consecutive frames to the 89-frame clip, with allowance for decode and write overhead. The point cloud option uses the fixed native-resolution Hypersim collection. A prior attempt on original DA-2K portraits reached the GPU memory limit.

The training ranges use 14,885 Hypersim or 4,889 Virtual KITTI 2 optimizer batches per epoch on one GPU, plus complete validation and checkpoint I/O each epoch. With only two post-first-batch intervals per projected run, the estimate uses a wide 0.37–0.56 s per training batch. Validation allowance is 0.06–0.145 s per Hypersim pair or 0.15–0.36 s per KITTI pair, around the measured ten-pair phases. The lower end allows loader startup to be amortized over the full split. These assumptions give measured-rate centers of about 10.4 days and 3.3 days. The Virtual KITTI 2 sample covers one scene and camera variation, and the KITTI validation sample spans five drives.

The official Hypersim recipe uses eight GPUs. This machine has one, so the range applies to the viable single-GPU configuration. For an eight-GPU run, measure representative training, validation, and checkpoint writes on the intended interconnect and storage at batch 4 per GPU. The current estimates make no eight-GPU scaling assumption. The samples took 4.4–26.1 seconds each end to end, and none reached the deadline. There were no new downloads for this round. Preparing the complete training sets is additional work.

### Historical comparison

These earlier measurements remain available for comparison. They do not supply the current timing ranges.

| Workload | Earlier observed elapsed time |
| --- | --- |
| Relative previews, 100 images | 25.4 s |
| Metric depth, 100 images | 30.5 s |
| Video, 89 frames | 28.4 s |
| Point clouds, 100 Hypersim images | 14.2 s |
| Demo, 100 independent requests | 60.8 s |
| DA-2K, 100 images and 207 annotated pairs | 15.8 s |
| Hypersim, 96 training and 100 validation pairs | 39.0 s |
| Virtual KITTI 2 with KITTI validation, 96 training and 100 validation pairs | 53.2 s |

### Start a selected run

Run from the project root with the [project environment](environment/README.md) active. First select a workload below. Give repeated managed runs distinct study names. Read a completed run with `depth-anything inspect <run-directory>`.

For the DA-2K image, demo and pairwise workloads, prepare the input lists once, then run the selected command.

```bash
benchmark="${DA_BENCHMARK_ROOT:?Set the extracted DA-2K directory}"
mkdir -p tmp/workload_lists
images=tmp/workload_lists/all_images.txt
indoor=tmp/workload_lists/indoor_images.txt
sed "s|^|$benchmark/|" assets/splits/da_benchmark/files/all_images.txt > "$images"
sed "s|^|$benchmark/|" assets/splits/da_benchmark/files/indoor_images.txt > "$indoor"

depth-anything image --encoder vitl --img-path "$images" --study benchmark_previews
depth-anything metric --encoder vitl --img-path "$indoor" --save-numpy --study indoor_predictions
python scripts/run_demo_batch.py --image-list "$images" --study demo_workload
python scripts/evaluate_depth_order.py --dataset-root "$benchmark" \
  --load-from "$DEPTH_ANYTHING_WEIGHTS/depth_anything_v2_vitl.pth" --study relative_benchmark
```

The bundled video runs independently:

```bash
depth-anything video --encoder vits --video-path assets/samples/videos/files/basketball.mp4 --study basketball_depth
```

For point clouds, rebase the recorded Hypersim sample names onto the local extraction containing those scenes:

```bash
hypersim="${HYPERSIM_IMAGE_ROOT:?Set the extracted Hypersim image root}"
mkdir -p tmp/workload_lists
clouds=tmp/workload_lists/four_scene_images.txt
sed "s|^|$hypersim/|" assets/splits/hypersim_images/files/four_scene_images.txt > "$clouds"
depth-anything pointcloud --encoder vits --img-path "$clouds" --study hypersim_clouds
```

The demo batch command starts the official loopback demo and checks the returned PNGs. It saves a timing record and removes its disposable downloads and service cache. The demo can also be opened interactively with `depth-anything demo --encoder vitl`. The pairwise benchmark uses the closer-point ordering described by the publisher and averages the scenario accuracies as in the paper. [Dataset annotations](https://huggingface.co/datasets/depth-anything/DA-2K) · [Paper, Table 14](https://arxiv.org/html/2406.09414v2#A3.T14)

For formal training, set each split variable below to a local text file containing the complete split with paths to the publisher image and depth files. These commands use the full 120-epoch recipe with one GPU. Set `DEPTH_GPU_COUNT=8` only on an allocated eight-GPU system after measuring that configuration.

```bash
DEPTH_GPU_COUNT=1 bash scripts/distributed_training.sh \
  --train-split "$HYPERSIM_TRAIN_SPLIT" --validation-split "$HYPERSIM_VALIDATION_SPLIT" \
  --study hypersim_finetuning

DEPTH_GPU_COUNT=1 bash scripts/distributed_training.sh --dataset vkitti --max-depth 80 \
  --train-split "$VKITTI_TRAIN_SPLIT" --validation-split "$KITTI_VALIDATION_SPLIT" \
  --study outdoor_finetuning
```

Full-split training and complete DA-2K scoring await selection. The timed samples above retain their configurations, data paths, and outputs for inspection.
