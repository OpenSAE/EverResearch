# CoTracker maintenance

## Purpose and main function

Record how this CoTracker snapshot was adopted and what could be verified.

## Scope of application

Use this page to trace relocated implementations, confirm the working commands, and identify inputs needed for benchmark and training runs.

This portable template includes offline maintenance. Configure the interpreter and data paths in your copied project.

| Original implementation | Active implementation and entry |
| --- | --- |
| `cotracker/datasets/` and the demo video reader | [Dataset readers](../datasets/video_tracking/) retain the installed `cotracker.datasets` imports. |
| `cotracker/models/` and `cotracker/predictor.py` | [Predictor and checkpoint code](../models/tracking/) and [network variants](../models/network/) retain the original Python imports. |
| `hubconf.py`, the demo scripts, and visualizer | [Factory functions](../base/tracking/hub_api.py), [tracking tasks](../tasks/tracking/), and [shared utilities](../base/tracking/shared/) support the managed tracking command and both original demo workflows. |
| `cotracker/evaluation/` and its seven recipes | [Evaluation](../tasks/evaluation/) is selected by `evaluate` with the [original preset names](../conf/tasks/evaluation/presets.yaml). |
| Two training scripts and trajectory losses | [Training and losses](../tasks/training/) run via `train-kubric` and `train-real-video`. [Slurm launchers](../scripts/training/) install a copy of the source used by the submitted job. |
| Notebook, Gradio app, example media, and Sphinx site | [Standalone examples](../scripts/examples/), [assets](../assets/), and [Sphinx source](code/sphinx/source/) support the same demonstrations and API pages. |

The offline command tracked 100 points over all 50 frames of the bundled apple clip with the released CoTracker3 weights on CUDA. Coordinate and visibility arrays matched the original implementation exactly. The original and current offline and streaming overlays had identical SHA-256 checksums within each mode. The reference readback covered arrays, the MP4, and the startup report. A separate invalid-query run verified rejection before formal computation.

The project and experiment checks passed with zero violations. The package built and loaded from outside the checkout. The sampling tests passed, the notebook's first tracking example and Gradio's grid callback rendered videos, and the Sphinx site built. The TAP-Vid command ran on one short clip with test annotations and the released offline weights. Both training command parsers loaded in the compatible Lightning environment. A local scheduler stand-in checked that all four Slurm launchers install their source snapshot and prepare the intended command.

Full benchmark reproduction requires the TAP-Vid or Dynamic Replica input specified by its recipe. Kubric training requires annotated data. The real-video loader is an upstream scaffold that requires a user-supplied dataset implementation and a TAPIR teacher checkpoint. Real Slurm submission also requires the original scheduler resources or equivalent local settings.

## Formal run choices

Reference timings were measured during adoption. Reproduce them with the data, weights, and commands below.

Source: [facebookresearch/co-tracker@82e02e8029](https://github.com/facebookresearch/co-tracker/tree/82e02e8029753ad4ef13cf06be7f4fc5facdda4d). Estimates come from the reference tests. Reproduce the checks in your copied checkout before selecting a full run.

The profiled machine is one NVIDIA GeForce RTX 5090 with 32 GB of memory, Python 3.12.15, and PyTorch 2.10.0 with CUDA 12.8. Timings include process startup, input and model checks, computation, and result writes. The GPU queue, data downloads, and sample preparation are separate. Each profile stops at approximately ten work units or after five minutes of elapsed execution.

| Formal run | Released inputs, full workload, and outputs | Timed sample | Estimated end-to-end time |
| --- | --- | --- | --- |
| Offline point tracks | Released CoTracker3 scaled offline weights. One pass over all **50 consecutive frames** of the publisher's 1296 × 720 apple clip. Query a 10 × 10 grid on frame zero. Writes coordinates and visibility to NPZ and a single MP4 overlay. | 10 consecutive frames in **4.60 s**. The built-in precheck took 1.66 s, then tracking and file writes took 0.83 s.  | **6–10 s** |
| Online point tracks | Same **50 frames** and grid, released scaled online weights. One sequential stream with 16-frame windows and an 8-frame stride. Writes one MP4 overlay. | 10 consecutive frames in **3.47 s**. First window at 1.98 s, then 0.41 s to start rendering and 0.61 s to write the MP4.  | **6–12 s** |
| TAP-Vid DAVIS, offline | All **30 real DAVIS validation clips**, 1,999 frames and 650 annotated trajectories, with the official first-visible query annotations, one pass using released scaled offline weights. Batch one and one loader worker. The evaluator scores joint queries on 256 × 256 images with the model operated at 384 × 512. Writes the effective configuration, average Jaccard, occlusion accuracy, visible-point accuracy at five thresholds, and a sample MP4. | 10 complete clips, 692 frames and 215 query tracks in **8.68 s**. The evaluator started at 4.26 s and finished in 3.77 s.  | **11–18 s** |
| TAP-Vid DAVIS, online | Same **30 annotated clips**, query mode, batch and worker count, using released scaled online weights and the online predictor's 16-frame windows. Writes the same benchmark products. | 10 complete clips, 692 frames and 215 query tracks in **10.45 s**. The evaluator started at 3.19 s and finished in 6.63 s.  | **17–28 s** |
| Interactive grid demo | **Eight publisher showcase clips** and the released scaled online weights. One independent local upload and grid-tracking request per clip. The model uses a 15 × 15 grid and 384 × 512 input. Returns eight MP4 previews. | All **eight requests and 744 output frames** in **55.75 s**. Local service startup 2.68 s. Individual upload, processing, download and readback took 3.77–11.45 s.  | **45–75 s** |
| Kubric supervised baseline | The publisher's CoTracker3 Kubric release contains **5,869 downloadable sequences** at 512 × 512 with 120 frames each. Train CoTracker3 online from random initialization with 50,000 scheduled optimizer steps, 64-frame inputs, 384 queries, batch one per GPU and ten loader workers per rank. Writes TensorBoard loss, evaluation and validation previews, periodic checkpoints, and a final model. | **13.91 s** to first-clip failure on the RTX 5090. The first forward pass started at 10.21 s and exhausted its 32 GB VRAM. Zero optimizer steps.  | **About 35 h online or 24 h offline** on 32 A100 80 GB GPUs, as reported by the authors. This machine needs the smaller input settings below. |
| Kubric supervised baseline, reduced memory | Same released corpus and 50,000-step online schedule, using **48 frames and 128 queries**. Batch one per GPU, ten loader workers per rank, bfloat16. Same outputs as the full-size supervised recipe. | 10 optimizer updates from six distinct official clips, two passes of five DAVIS and five RGB-Stacking validation clips, and final weights in **52.63 s**. First update at 12.17 s, then about 0.50 s per update outside validation.  | **6–12 h** on one RTX 5090 after the complete dataset and validation are staged. The final-only splits still need calibration. |
| Real-video pseudo-label fine-tuning | Published online recipe, **up to 15,000 real clips and 15,000 scheduled optimizer steps**. Batch one per GPU, ten workers per rank, 64 frames and 384 points per clip. Initialize with the released Kubric online baseline, use CoTracker2.1, both Kubric baseline variants and TAPIR for pseudo-labels. Writes training logs, benchmark evaluations, checkpoints and a final model. | **7.38 s** to the dataset loader's unconditional rejection, after both official validation sets loaded. Zero optimizer steps.  | No local range. A compatible real-video collection and loader are needed before the first representative training step can run. |

The timed DAVIS suites use the official pickle from DeepMind, preserving all frames and annotations for the measured clips. The profile selects ten clips spread by frame count × annotated tracks and loads the whole official pickle before selecting records. The estimates keep startup, first-clip initialization and result writing fixed and scale the remaining evaluation by approximately three, reflecting the measured 14,150 and full 42,200 frame-query pairs. The tracking estimates keep a single model startup and use the observed rendering cost and number of windows in the 50-frame clip. Both tracking profiles processed ten input frames. The preserved CLI visualizer intro and trimming produced a 16-frame preview in each case. Measurements apply to the joint-query, first-visible presets. The online evaluator follows the online predictor branch in this snapshot. The offline publisher recipe also supports single-point evaluation by setting `single_point=True`, which changes the compute workload. [Official TAP-Vid datasets and protocols](https://github.com/google-deepmind/tapnet/tree/main/tapnet/tapvid)

Additional evaluation presets cover DAVIS strided queries, RGB-Stacking first or strided queries (50 released clips), Kinetics first-visible queries (1,000 annotated source clips), RoboTAP first-visible queries, and Dynamic Replica validation (20 sequences, first 300 left-camera frames and 256 tracks per sequence). The official DAVIS and RGB-Stacking archives downloaded in 50.8 s and 8.5 s respectively. The unpacked array files occupy about 4.7 GiB combined. Kinetics requires reconstructing evaluator shards from licensed source MP4s and the published CSV. RoboTAP's archive alone is 13.56 GB. The authorized Dynamic Replica download needs accepted terms and up to 106 GB for the publisher's unpacked validation package with all annotation types. The DAVIS timing ranges apply to the two first-visible rows above. Data access evidence · [Dynamic Replica publisher setup](https://github.com/facebookresearch/dynamic_stereo#download-the-dynamic-replica-dataset)

The CoTracker3 paper reports about 35 hours for the online Kubric baseline and 24 hours for offline on 32 A100 80 GB GPUs. The public offline recipe uses a 60-frame upper limit, 512 queries and random query frames. The RTX 5090 attempt used the full online recipe's batch, precision and input shape. The reduced profile uses the paper's 48-frame, 128-query option for smaller GPUs. Under the public loader the selected Kubric corpus is repeated four times per epoch. At the full online workload on one GPU this is 23,476 candidate batches per epoch before any failed sample filtering. The trainer's published command has startup validation after the first successful update, periodic checkpoint and evaluation every five epochs, an overlay cadence of 200 optimizer steps, and a final validation pass. The final validation opens DAVIS, RGB-Stacking, Kinetics, RoboTAP and Dynamic Replica. The reduced estimate uses 0.43–0.75 s per update for about six to ten and a half hours of training. It budgets up to another hour for startup, validation, encoding and checkpoint I/O. The timing sample measured 17.51 s for startup validation, 14.94 s for final subset validation, and about 1.49 s for writing the final weights and entering final validation. The extra final-only split inputs need storage, enough host memory for the loader and a dedicated validation profile before this overhead can be confirmed. TensorBoard scalar metrics were written. The optional video events require a compatible MoviePy installation. [Kubric dataset release](https://huggingface.co/datasets/facebook/CoTracker3_Kubric) · [CoTracker3 paper appendix](https://openaccess.thecvf.com/content/ICCV2025/supplemental/Karaev_CoTracker3_Simpler_and_ICCV_2025_supplemental.pdf)

### Start a selected run

Run from the project root using the [project environment](environment/README.md). The `COTRACKER_OUTPUT_ROOT` variable names a writable destination for the upstream commands. Use a fresh study name with managed `track` and open its products with `python main.py inspect <study-directory>`.

```bash
weights="${COTRACKER_WEIGHTS:?Set the official checkpoint directory}"
apple=assets/videos/apple/files/apple.mp4
tapvid="${TAPVID_ROOT:?Set the TAP-Vid data directory}"
output=${COTRACKER_OUTPUT_ROOT:?Set a writable directory for upstream outputs}

python main.py track --video "$apple" --device cuda --checkpoint "$weights/scaled_offline.pth" \
  --grid-size 10 --subname apple_offline
python main.py online-demo --video_path "$apple" --checkpoint "$weights/scaled_online.pth" \
  --grid_size 10 --output-dir "$output/apple_online"

python main.py evaluate --config-name eval_tapvid_davis_first \
  exp_dir="$output/davis_offline" dataset_root="$tapvid" checkpoint="$weights/scaled_offline.pth" \
  offline_model=True window_len=60
python main.py evaluate --config-name eval_tapvid_davis_first \
  exp_dir="$output/davis_online" dataset_root="$tapvid" checkpoint="$weights/scaled_online.pth"

COTRACKER_ONLINE_CHECKPOINT="$weights/scaled_online.pth" python scripts/examples/gradio_demo.py
```

For supervised training, set `COTRACKER_TRAINING_DATA` to a root with `kubric/kubric_movi_f_120_frames_dense/movi_f/<sequence>/frames/`, each sequence's `<sequence>.npy` coordinates and visibility, and the validation data at the paths in the [training loader](../base/tracking/shared/train_utils.py). The ten prepared training sequences use about 1.8 GB. The complete prepared release is on the order of 1 TB for RGB frames and annotations, estimated from that sample. The runner opens its final validation splits at startup. Stage their required inputs before starting the formal command. Use the A100 results above for the paper's 32-GPU recipe with eight GPUs per node and `--num_nodes 4` in a configured distributed environment. The command below uses the reduced input settings for one RTX 5090 with the project training dependencies. The timing environment used Lightning 1.6.0 and TorchMetrics 0.11.4 from the existing compatibility directory `/tmp/cotracker-training-deps` on `PYTHONPATH`. Pass only the intended GPU using `CUDA_VISIBLE_DEVICES`. For the full paper configuration, change `--sequence_len` to `64` and `--traj_per_sample` to `384` with an appropriately sized GPU per rank.

```bash
data=${COTRACKER_TRAINING_DATA:?Set the full Kubric and validation data root}
CUDA_VISIBLE_DEVICES=0 python main.py train-kubric --batch_size 1 --num_workers 10 --num_steps 50000 \
  --ckpt_path "$output/kubric_online" --model_name cotracker_three --save_freq 200 --sequence_len 48 \
  --eval_datasets tapvid_davis_first tapvid_stacking --traj_per_sample 128 --sliding_window_len 16 \
  --train_datasets kubric --save_every_n_epoch 5 --evaluate_every_n_epoch 5 --model_stride 4 \
  --dataset_root "$data" --num_nodes 1 --num_virtual_tracks 64 --mixed_precision --corr_radius 3 \
  --wdecay 0.0005 --linear_layer_for_vis_conf --validate_at_start --add_huber_loss
```

For real-video fine-tuning, first provide a loader implementing the project video batch interface and place the teacher weights at the runner's configured paths. The CoTracker2.1 weights, offline Kubric baseline, and online Kubric baseline are at `checkpoints/cotracker2v1.pth`, `checkpoints/baseline_offline.pth`, and `checkpoints/baseline_online.pth` relative to the working directory except where `--restore_ckpt` supplies the matching variant. Install TAPIR and set `COTRACKER_TAPIR_CHECKPOINT` to the released Torch panning checkpoint. A local calibration must observe actual data loading, pseudo-label inference, optimizer steps, validation and checkpoint writes. [CoTracker3 weights](https://huggingface.co/facebook/cotracker3) · [CoTracker2.1 weights](https://huggingface.co/facebook/cotracker) · [TAPIR weights](https://github.com/google-deepmind/tapnet)

```bash
CUDA_VISIBLE_DEVICES=0 python main.py train-real-video --batch_size 1 --num_workers 10 --num_steps 15000 \
  --ckpt_path "$output/real_video_online" --model_name cotracker_three --save_freq 200 --sequence_len 64 \
  --eval_datasets tapvid_stacking tapvid_davis_first --traj_per_sample 384 --save_every_n_epoch 15 \
  --evaluate_every_n_epoch 15 --model_stride 4 --dataset_root "$data" --num_nodes 1 --real_data_splits 0 \
  --num_virtual_tracks 64 --mixed_precision --random_frame_rate --restore_ckpt "$weights/baseline_online.pth" \
  --lr 0.00005 --real_data_filter_sift --validate_at_start --sliding_window_len 16 --limit_samples 15000
```

The [experiment page](experiment.md#bounded-formal-run-profiles) links to the profiling commands, observed progress, and results.
