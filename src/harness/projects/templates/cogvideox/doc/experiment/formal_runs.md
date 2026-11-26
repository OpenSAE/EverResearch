# CogVideoX formal run choices

## Purpose and main function

Choose a complete generation, fine-tuning, or video-processing workload and use its measured runtime to plan GPU time and storage.

## Scope of application

Use this guide from the project root with the [project environment](../environment/README.md) active. The full workloads are ready for selection. The linked evidence comes from bounded runtime profiles.

## Diffusers workloads

The hardware for local measurements is one NVIDIA GeForce RTX 5090 with 32 GB of VRAM, Python 3.12.15, PyTorch 2.11.0 with CUDA 12.8, Diffusers 0.35.2, Transformers 4.57.1, and Accelerate 1.11.0. Generation uses one request per process, one video per request, the project's DPM scheduler and sequential CPU offload. Times include each process startup, local model loading, calculation and artifact writes. Checkpoint transfer and media preparation have separate measurements. The 25.3 MB source dataset downloaded in **10.4 s**. All 69 first frames took **3.7 s** to extract and all 69 video conditions took **36.5 s** to encode with FFmpeg using one thread. The two model snapshots finished in **6 min 41 s** and **6 min 50 s** during concurrent transfers after an initial partial HTTP download. The measured process ranges assume locally cached weights.

| Formal run | Complete workload and product | Measured sample and estimated wall time |
| --- | --- | --- |
| Text-to-video preview batch | All **69** publisher captions, one pass with CogVideoX-2B at 720 × 480, 49 frames, 8 fps, 50 denoising steps and FP16. Writes 69 newly generated MP4s. | Two reused complete requests took **236.0 s** total, at **116.0–119.9 s** each. Startup took **7.1–8.3 s** and export **0.55–0.86 s** per clip. Estimated **1.9–2.7 h**. Goat song · Frying pan |
| Image-to-video preview batch | All **69** publisher captions paired with their source first frame, one pass with CogVideoX-5B-I2V at 720 × 480, 49 frames, 8 fps, 50 denoising steps and BF16. Writes 69 image-conditioned MP4s. | One reused complete request took **268.6 s**, including **6.9 s** startup and **0.48 s** export. Estimated **4.4–6.4 h**. Mechanical towers |
| Video-to-video regeneration batch | All **69** publisher caption and source clip pairs, one pass with CogVideoX-2B at 720 × 480 and FP16. Each source is resampled to 49 frames at 8 fps. The pipeline's 0.8 strength runs 40 of the 50 configured denoising steps. Writes 69 regenerated MP4s. | Two reused complete requests took **209.4 s** total, at **102.4–106.9 s** per clip. The 40 denoising steps of each clip took **67–69 s**. Estimated **1.7–2.5 h**. Goat song · Mechanical towers |
| Train a text-to-video LoRA adapter | **66 training clips** and **3 held-out caption prompts**, 10 epochs, batch 1, eight workers, CogVideoX-2B FP16 at 49 × 480 × 720. Runs 660 optimizer steps, saves every 200 steps and at completion, and generates 12 preview videos across three scheduled validations and the final validation. | **296.6 s** yielded **7 optimizer steps and 2 complete validation clips**. The time limit stopped the third validation clip during denoising. Startup and cold preparation took **36 s** through the first optimizer batch launch. Steady batches took about **3 s** and complete validation clips **91–94 s** each. Estimated **45–70 min**. Bounded profile |
| Encode and reconstruct source video | All **69 source clips**, resampled to 49 frames, one clip per process with the official CogVideoX-2B video autoencoder (VAE) in BF16. Writes 69 latent tensors and 69 reconstructed MP4s. | **10 clips, 490 processed frames**, in **88.4 s** total, with **7.9–10.8 s** per clip. Reused four complete profiles and added six. Estimated **9–14 min** and about **120 MB** of outputs. The MP4s contain 49 frames each at 8 fps. The exporter aligns 640 × 360 inputs to 640 × 368. Combined runtime evidence |

The workload uses the complete Steamboat Willie publisher snapshot. It contains 69 aligned, distinct video paths and 69 nonempty captions. The project uses it for style adaptation and generation previews. The timing sample represents this animation collection. Stream verification found 68 clips with 195 frames at 30 fps and one clip with 55 frames. The 49-frame processing recipe applies to all clips after padding the short input. All raw source videos are 640 × 360. [Publisher snapshot](https://huggingface.co/datasets/Wild-Heart/Disney-VideoGeneration-Dataset/tree/823c1f015e7ced7fffb8ad44881f792195114386)

Each timing workload targets about ten real work units and ends within five minutes of actual operation, including startup and the automatic precheck. Weight download, media preparation and GPU queue time are separate. A complete clip, including denoising, decode and export, is one generation unit. The remaining budget after each mode's one or two complete requests was shorter than another observed clip. The ranges extrapolate the selected profiles to all 69 source entries and allow for startup, cache and I/O variability. The earlier second image-to-video request remains a historical result because the two complete requests together took 538.4 s. Historical image-to-video run

The instrumented VAE run spent 4.4 s in startup before its first model load. Its two model loads took 0.70 s combined. Maximum allocated GPU memory was about 10.3 GiB. VAE stages

### Prepare local inputs

Use a shared data location for the pinned source and prepared assets. The public Hugging Face repositories can be read without a token. The model snapshots are about 13.8 GB and 21.6 GB. These commands populate the configured Hugging Face cache and place the video inputs in the shared data directory. Activate the environment described in the project environment guide before running the commands.

```bash
export COG_DATA="${COG_RUN_DATA_ROOT:-$PWD/../data/cogvideox}/steamboat"
export COG_SPLIT="${COG_RUN_DATA_ROOT:-$PWD/../data/cogvideox}/steamboat_prepared"
small_model=zai-org/CogVideoX-2b
image_model=zai-org/CogVideoX-5b-I2V
small_revision=1137dacfc2c9c012bed6a0793f4ecf2ca8e7ba01
image_revision=a6f0f4858a8395e7429d82493864ce92bf73af11

hf download Wild-Heart/Disney-VideoGeneration-Dataset --repo-type dataset \
  --revision 823c1f015e7ced7fffb8ad44881f792195114386 \
  --include prompt.txt videos.txt 'videos/*' --local-dir "$COG_DATA"

snapshot_components=(model_index.json 'scheduler/*' 'text_encoder/*' 'tokenizer/*' 'transformer/*' 'vae/*')
small_weights=$(hf download "$small_model" --revision "$small_revision" --include "${snapshot_components[@]}" --quiet)
image_weights=$(hf download "$image_model" --revision "$image_revision" --include "${snapshot_components[@]}" --quiet)
```

The generation precheck requires a local directory with the model basename. Build local directories with links to the downloaded snapshot's components. The named directories also make the CLI model selection reproducible when the Hub branches advance.

```bash
model_root="${COG_RUN_DATA_ROOT:-$PWD/../data/cogvideox}/checkpoints"
small_local="$model_root/CogVideoX-2b"
image_local="$model_root/CogVideoX-5b-I2V"
mkdir -p "$small_local" "$image_local"
for component in model_index.json scheduler text_encoder tokenizer transformer vae; do
  ln -sfn "$small_weights/$component" "$small_local/$component"
  ln -sfn "$image_weights/$component" "$image_local/$component"
done
```

### Run one complete generation mode

Set `mode` to `t2v`, `i2v`, or `v2v` and choose a new absolute results directory. The filenames preserve the source clip identifiers for alignment with the two publisher lists. For an independently inspectable single request, omit `--output_path`, add a descriptive `--purpose` and `--execution`, then open the printed run directory with `cogvideo inspect`.

```bash
set -e
mode=t2v
export COG_OUTPUT=/absolute/path/to/selected/preview_batch
mkdir -p "$COG_OUTPUT" "$COG_SPLIT/first_frames" "$COG_SPLIT/video_conditions"
mapfile -t clips < "$COG_DATA/videos.txt"
mapfile -t captions < "$COG_DATA/prompt.txt"
test "${#clips[@]}" -eq 69
test "${#captions[@]}" -eq 69

for index in "${!clips[@]}"; do
  clip="${clips[$index]}"
  clip_name="${clip##*/}"
  stem="${clip_name%.mp4}"
  model="$small_local"
  dtype=float16
  media=()
  case "$mode" in
    t2v) ;;
    i2v)
      model="$image_local"
      dtype=bfloat16
      image="$COG_SPLIT/first_frames/$stem.png"
      ffmpeg -nostdin -v error -y -threads 1 -i "$COG_DATA/$clip" -frames:v 1 "$image"
      media=(--image_or_video_path "$image")
      ;;
    v2v)
      video="$COG_SPLIT/video_conditions/$clip_name"
      ffmpeg -nostdin -v error -y -threads 1 -i "$COG_DATA/$clip" -an \
        -vf 'fps=8,tpad=stop_mode=clone:stop_duration=6.125' -frames:v 49 \
        -c:v libx264 -threads 1 -pix_fmt yuv420p "$video"
      media=(--image_or_video_path "$video")
      ;;
    *) exit 2 ;;
  esac
  cogvideo generate --model_path "$model" --generate_type "$mode" \
    --prompt "${captions[$index]}" --num_frames 49 --fps 8 \
    --num_inference_steps 50 --num_videos_per_prompt 1 --dtype "$dtype" \
    --seed 42 "${media[@]}" --output_path "$COG_OUTPUT/$clip_name"
done
```

For the video-to-video pipeline, the number of decoded input frames determines the number of frames used for inference. The resampling command keeps the window at 49 frames. It repeats the last available frame for the one short publisher clip. The text-to-video and image-to-video pipelines use `--num_frames` directly.

### Run the complete Diffusers LoRA recipe

Materialize the [held-out positions](../../assets/splits/steamboat_willie/README.md) before the training command. Paths in the source list are relative to the generated manifests. The trainer caches VAE latents and prompt embeddings in the prepared data directory at first use. Reserve working space for that cache, the two retained checkpoints, and the validation MP4s.

```bash
python - <<'PY'
import os
from pathlib import Path

source = Path(os.environ["COG_DATA"])
split = Path(os.environ["COG_SPLIT"])
split.mkdir(parents=True, exist_ok=True)
if not (split / "videos").exists():
    (split / "videos").symlink_to(source / "videos", target_is_directory=True)
positions = Path("assets/splits/steamboat_willie/files/validation_positions.txt")
held_out = {int(value) for value in positions.read_text().splitlines()}
prompts = (source / "prompt.txt").read_text().splitlines()
videos = (source / "videos.txt").read_text().splitlines()
rows = list(enumerate(zip(prompts, videos, strict=True), 1))

for phase, take_held_out in (("train", False), ("validation", True)):
    pairs = [pair for position, pair in rows if (position in held_out) == take_held_out]
    (split / f"{phase}_prompts.txt").write_text("".join(prompt + "\n" for prompt, _ in pairs))
    (split / f"{phase}_videos.txt").write_text("".join(path + "\n" for _, path in pairs))
PY

cogvideo-finetune --model_path "$small_weights" --model_name cogvideox-t2v \
  --model_type t2v --training_type lora --output_dir /absolute/path/to/selected/lora_run \
  --data_root "$COG_SPLIT" --caption_column train_prompts.txt --video_column train_videos.txt \
  --train_resolution 49x480x720 --train_epochs 10 --batch_size 1 --num_workers 8 \
  --gradient_accumulation_steps 1 --mixed_precision fp16 --seed 42 --rank 128 --lora_alpha 64 \
  --checkpointing_steps 200 --checkpointing_limit 2 --report_to tensorboard \
  --do_validation true --validation_dir "$COG_SPLIT" --validation_prompts validation_prompts.txt \
  --validation_steps 200 --gen_fps 8
```

Checkpoint outputs include adapter weights and optimizer state. Validation saves qualitative preview videos. Each validation call generates a clip with the pipeline's 50-step default and exports the result. See the [full fine-tuning guide](../code/diffusers_finetuning/README.md) for other variants.

The timing sample used seven clips spaced across the 66-item training list and all three held-out prompts in the same run. It wrote a roughly 708 MB checkpoint after the seventh update and retained two completed validation clips at the deadline. The estimate budgets 2.5–3.6 s for each of the 660 optimizer steps, 80–110 s for each of the 12 complete validation previews, and about 2–3 minutes for the full cold latent cache. It includes startup, four checkpoint writes and timer uncertainty. The estimate covers a single RTX 5090. Effective settings and retained outputs

The first launch reached the host memory limit during model loading. Loading the frozen text encoder and video autoencoder in the configured training precision let the public fine-tuning command complete its optimizer steps and produce validation videos on this approximately 30 GiB host. The transformer and adapter initialization keep their existing precision. Initial launch and bounded timeline

### Run the VAE reconstruction batch

This entry point uses the VAE component of the same official 2B snapshot. It can run independently of generation or fine-tuning.

```bash
set -e
export COG_OUTPUT=/absolute/path/to/selected/vae_reconstructions
mkdir -p "$COG_OUTPUT" "$COG_SPLIT/video_conditions"
while IFS= read -r clip || test -n "$clip"; do
  clip_name="${clip##*/}"
  stem="${clip_name%.mp4}"
  video="$COG_SPLIT/video_conditions/$clip_name"
  run="$COG_OUTPUT/$stem"
  mkdir -p "$run"
  ffmpeg -nostdin -v error -y -threads 1 -i "$COG_DATA/$clip" -an \
        -vf 'fps=8,tpad=stop_mode=clone:stop_duration=6.125' -frames:v 49 \
    -c:v libx264 -threads 1 -pix_fmt yuv420p "$video"
  python scripts/inference/cli_vae_demo.py --model_path "$small_weights/vae" \
    --video_path "$video" --output_path "$run" --mode both --dtype bfloat16
done < "$COG_DATA/videos.txt"
```

## Other public workflows

These include separate weights, dependencies, or execution environments. The local 2B timing range applies to the Diffusers invocation and its specified settings.

| Workflow | Priority workload and products | Runtime evidence and remaining requirement |
| --- | --- | --- |
| Diffusers image-to-video LoRA | Use the official 5B-I2V base, the same 66 training clips and three held-out prompts with their first frames, 10 epochs, batch 1, eight workers and BF16. Writes adapter states and 12 preview MP4s. | The upstream guide lists 24 GB VRAM for this model and recipe. A host must also hold the model components during preparation. Profile cold preprocessing, 25 optimizer steps, all three held-out requests and one checkpoint before estimating the 660-step workload. |
| Diffusers full transformer fine-tuning | Use CogVideoX-2B and the same 66 clips, 10 epochs, batch 1, eight workers and a ZeRO-2 optimizer-offload configuration. Writes the full trained transformer and resumable states. | The upstream hardware table lists 17 GB of GPU memory for the one-GPU optimizer-offload setup. This machine has about 30 GiB of physical RAM. The FP32 master weights and Adam states also need CPU memory. Time with a larger-memory host and verify checkpoint consolidation and validation there. |
| SAT text-to-video sampling | Use the four bundled SAT prompts and official CogVideoX1.5-5B-SAT T2V weights, batch 1, BF16, 22 latent frames, 768 × 1,360 output canvas, 16 fps and 50 denoising steps. Writes four MP4s. | The sample command imports and opens its help. Measure all four prompts with the SAT checkpoint, VAE and T5 paths resolved in the configuration. The T2V checkpoint bundle requires about 25.8 GB of downloads. The measured SAT result covers command startup. |
| SAT LoRA training | Use official small SAT text weights and the 66/3 clip split in SAT's matching `labels/` and `videos/` form. Choose the supplied 1,000-update recipe with microbatch 2 on one GPU, 2,000 training sample slots, eight workers, one validation batch every 100 steps and states at steps 500 and 1,000. | The training command imports and opens its help. The separate Tsinghua SAT transformer and VAE weights and a runnable DeepSpeed configuration are required to time the actual train step, the validation event and checkpoint writes. |
| DDIM inversion and reconstruction | Use the 69 prepared 49-frame conditions and paired captions with the official CogVideoX-5B text checkpoint, one video at a time at 720 × 480, 8 fps and 50 steps in each direction. Writes 69 inversion and 69 reconstruction MP4s. | The command opens its help. The script requires a 5B text checkpoint with rotary position embeddings and places the entire model on CUDA. Use a ≥48 GB GPU to calibrate at least two complete inverse and reconstruction pairs, including both video writes. |
| Composite web demo | Use the official CogVideoX-5B checkpoint with the three bundled real input videos. Submit three independent video-to-video requests, one per clip, with 50 configured steps and strength 0.8. Optionally select RIFE frame interpolation and Real-ESRGAN upscaling as a separate settings profile. Writes the preview MP4 and optional processed video. | The mounted environment lacks Gradio, MoviePy and OpenAI client dependencies. The demo also needs the local RIFE and Real-ESRGAN assets and loads multiple models on CUDA. Use the documented demo environment and time launch, each request and each output variant before estimating wall time. |
| Video captioning | Use the official CogVLM2-Caption checkpoint and the three bundled video clips, one request per clip with the included `Please describe this video in detail.` prompt. Captures three captions for review. | This script depends on the caption-specific stack with Transformers 4.42.4. That differs from the measured generation environment. On a compatible GPU and environment, time startup and three separate requests after obtaining the 25 GB caption checkpoint. |
| VEnhancer | Use the first three outputs from the Steamboat Willie text-to-video batch, official `venhancer_paper.pt`, batch 1, 24 fps target, 2× upscale, fast solver with 15 steps. Writes three enhanced videos. | The [project tutorial](../code/video_enhancement/README.md) reports 40–50 minutes for one six-second clip on an A100 with about 60 GB of VRAM in its default setup. Budget this reference as **2–2.5 hours** for three sequential clips plus initial setup. The local 32 GB GPU cannot calibrate the publisher's memory requirement. |

The training variants follow the [Diffusers guide](../code/diffusers_finetuning/README.md). For image-conditioned LoRA, prepare the same manifests in a separate data directory so each model and precision has its own prompt embedding cache. Change the main training command to `--model_path "$image_weights" --model_name cogvideox-i2v --model_type i2v --mixed_precision bf16`. Training can extract the conditioning image from each source video. Prepare the held-out first frames with FFmpeg, list them in the validation order, and pass `--validation_images validation_images.txt`. For full fine-tuning on a host with adequate CPU memory, use the supplied one-GPU optimizer-offload configuration. This recipe selects the checkpoint's full transformer for training and defers preview validation to a separate run after consolidation.

```bash
accelerate launch --num_processes 1 --num_machines 1 --use_deepspeed \
  --deepspeed_config_file scripts/fine_tuning/settings/zero_two_offload.yaml \
  --mixed_precision bf16 -m finetune.train --model_path "$small_weights" \
  --model_name cogvideox-t2v --model_type t2v --training_type sft \
  --output_dir /absolute/path/to/selected/full_finetune --data_root "$COG_SPLIT" \
  --caption_column train_prompts.txt --video_column train_videos.txt \
  --train_resolution 49x480x720 --train_epochs 10 --batch_size 1 --num_workers 8 \
  --gradient_accumulation_steps 1 --mixed_precision bf16 --seed 42 \
  --checkpointing_steps 200 --checkpointing_limit 2 --report_to tensorboard \
  --do_validation false
```

For SAT sampling, point the supplied settings to the T2V components in the official SAT snapshot. Use a writable directory outside the repository for the overlay and the four sample outputs.

```bash
sat_weights=$(hf download zai-org/CogVideoX1.5-5B-SAT \
  --revision 5b0363881e1546dcbf775739a5ef94790da383cd \
  --include 'transformer_t2v/*' 't5-v1_1-xxl/*' 'vae/*' --quiet)
export SAT_WEIGHTS="$sat_weights"
export COG_OUTPUT=/absolute/path/to/sat_samples
mkdir -p "$COG_OUTPUT"

python - <<'PYCONFIG'
import json
import os
from pathlib import Path

weights = Path(os.environ["SAT_WEIGHTS"])
output = Path(os.environ["COG_OUTPUT"])
overlay = {
    "args": {"load": str(weights / "transformer_t2v"), "output_dir": str(output)},
    "model": {
        "first_stage_config": {"params": {"ckpt_path": str(weights / "vae/3d-vae.pt")}},
        "conditioner_config": {
            "params": {
                "emb_models": [{
                    "target": "sgm.modules.encoders.modules.FrozenT5Embedder",
                    "is_trainable": False,
                    "input_key": "txt",
                    "ucg_rate": 0.1,
                    "params": {"model_dir": str(weights / "t5-v1_1-xxl"), "max_length": 224},
                }],
            },
        },
    },
}
(output / "sampling_overlay.json").write_text(json.dumps(overlay, indent=2) + "\n")
PYCONFIG

WORLD_SIZE=1 RANK=0 LOCAL_RANK=0 LOCAL_WORLD_SIZE=1 \
  python -m cogvideo_sat_task.sample_video --seed 42 --base \
  scripts/sat_workflows/settings/next_large_text.yaml \
  scripts/sat_workflows/settings/inference.yaml "$COG_OUTPUT/sampling_overlay.json"
```

SAT training uses `bash scripts/sat_workflows/train_single_gpu.sh` with the small text LoRA and supervised training settings. Set the local transformer, VAE and T5 paths and the two SAT data directories as described in the [SAT guide](../code/sat_workflows/README.md). The SAT source and Diffusers fine-tuning use different checkpoint formats.

For each prepared inversion clip and caption, run

```bash
mkdir -p "$COG_OUTPUT"
python scripts/inference/ddim_inversion.py --model_path zai-org/CogVideoX-5b \
  --video_path "$VIDEO_CONDITION" --prompt "$PUBLISHER_CAPTION" \
  --output_path "$COG_OUTPUT" --max_num_frames 49 --num_inference_steps 50 \
  --width 720 --height 480 --fps 8 --dtype bf16
```

The composite demo starts with `python scripts/composite_demo/web_demo.py` after its [environment setup](../../scripts/composite_demo/README.md). Its complete input workload is the three clips under `assets/media/composite_examples/files/example_videos/`. For a caption request, place a link named `test.mp4` in that process's working directory and run `python /absolute/path/to/CogVideoStrictAdoption/scripts/caption/video_caption.py`, capturing its output. [Caption setup](../code/caption/README.md)

After the text-to-video batch, start enhancement with the upstream `python enhance_a_video.py --input_path "$VIDEO" --prompt "$SHORT_CAPTION" --target_fps 24 --up_scale 2 --solver_mode fast --version v1 --save_dir "$COG_OUTPUT"` command after installing the pinned tutorial stack. Use the generated previews as inputs so resolution, frame duration and export work match the planned workload. [Upstream VEnhancer](https://github.com/Vchitect/VEnhancer)

The [README inventory](../../README.md#tools) also lists checkpoint conversion and prompt service examples. Their work scales with the supplied checkpoint or service requests. Weight conversion takes the result of a selected training run. Parallel and quantized variants of generation use the [provided examples](../../README.md#inference), and their estimates require timing the selected configuration and hardware.
