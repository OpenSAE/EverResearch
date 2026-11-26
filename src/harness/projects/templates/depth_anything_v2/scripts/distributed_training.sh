#!/usr/bin/env bash
# Launch the upstream metric training recipe through the maintained training entry.
# Run from the workspace after installing the training extra and preparing split lists.
set -euo pipefail

python -m torch.distributed.run --standalone --nproc-per-node="${DEPTH_GPU_COUNT:-8}" \
    -m depth_anything_v2.research train \
    --epochs 120 --encoder vitl --bs 4 --lr 0.000005 --dataset hypersim \
    --img-size 518 --min-depth 0.001 --max-depth 20 \
    --pretrained-from "${DEPTH_ANYTHING_WEIGHTS:-checkpoints}/depth_anything_v2_vitl.pth" "$@"
