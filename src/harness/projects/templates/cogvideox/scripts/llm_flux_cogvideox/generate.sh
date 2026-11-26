#!/bin/bash

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

NUM_VIDEOS=10
INFERENCE_STEPS=50
GUIDANCE_SCALE=7.0
OUTPUT_DIR_PREFIX="outputs/gpu_"
LOG_DIR_PREFIX="logs/gpu_"

VIDEO_MODEL_PATH=${VIDEO_MODEL_PATH:-THUDM/CogVideoX-5B-I2V}
LLM_MODEL_PATH=${LLM_MODEL_PATH:-meta-llama/Meta-Llama-3.1-8B-Instruct}
IMAGE_MODEL_PATH=${IMAGE_MODEL_PATH:-black-forest-labs/FLUX.1-dev}

CUDA_DEVICES=${CUDA_VISIBLE_DEVICES:-"0"}

IFS=',' read -r -a GPU_ARRAY <<< "$CUDA_DEVICES"

mkdir -p "$(dirname -- "$LOG_DIR_PREFIX")" "$(dirname -- "$OUTPUT_DIR_PREFIX")"

for i in "${!GPU_ARRAY[@]}"
do
    GPU=${GPU_ARRAY[$i]}
    echo "Starting task on GPU $GPU..."
    CUDA_VISIBLE_DEVICES=$GPU nohup python3 "$script_dir/llm_flux_cogvideox.py" \
    --caption_generator_model_id "$LLM_MODEL_PATH" \
    --image_generator_model_id "$IMAGE_MODEL_PATH" \
    --model_path "$VIDEO_MODEL_PATH" \
    --num_videos $NUM_VIDEOS \
    --image_generator_num_inference_steps $INFERENCE_STEPS \
    --guidance_scale $GUIDANCE_SCALE \
    --use_dynamic_cfg \
    --output_dir ${OUTPUT_DIR_PREFIX}${GPU} \
    > ${LOG_DIR_PREFIX}${GPU}.log 2>&1 &
done
