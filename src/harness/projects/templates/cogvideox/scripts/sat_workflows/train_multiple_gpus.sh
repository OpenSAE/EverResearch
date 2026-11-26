#! /bin/bash

echo "RUN on $(hostname), CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

run_cmd="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True torchrun --standalone --nproc_per_node=8 -m cogvideo_sat_task.train_video --base scripts/sat_workflows/settings/large_image_lora.yaml scripts/sat_workflows/settings/supervised_training.yaml --seed $RANDOM"

echo ${run_cmd}
eval ${run_cmd}

echo "DONE on `hostname`"
