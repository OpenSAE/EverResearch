#!/bin/bash
# Submit the original multi-node job with a snapshot of this checkout.
set -euo pipefail

EXP_DIR=$1
EXP_NAME=$2
DATE=$3
DATASET_ROOT=$4
NUM_STEPS=$5


project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
mkdir -p -- "${EXP_DIR}/${DATE}_${EXP_NAME}/logs"
run_directory=$(cd -- "${EXP_DIR}/${DATE}_${EXP_NAME}" && pwd)
snapshot="${run_directory}/cotracker3"
mkdir -- "$snapshot"
for component in base datasets models tasks conf setup.py pyproject.toml README.md LICENSE.md; do
    cp -a -- "${project_root}/${component}" "$snapshot/"
done
python -m pip install --no-deps --target "${snapshot}/.packages" "$snapshot"
export PYTHONPATH="${snapshot}/.packages${PYTHONPATH:+:$PYTHONPATH}"
printf -v scheduler_output '%q' "$run_directory"
teacher_checkpoint="${COTRACKER_BASELINE_CHECKPOINT:-${project_root}/../data/cotracker_research/baseline_offline.pth}"
printf -v scheduler_checkpoint '%q' "$teacher_checkpoint"
printf -v scheduler_data '%q' "$DATASET_ROOT"

sbatch --comment=${EXP_NAME} --partition=learn --account=repligen --qos=repligen --time=120:00:00 --gpus-per-node=8 --nodes=4 --ntasks-per-node=8 \
--job-name=${EXP_NAME} --cpus-per-task=10 --signal=USR1@60 --open-mode=append \
--output="${run_directory}/logs/%j_%x_%A_%a_%N.out" \
--error="${run_directory}/logs/%j_%x_%A_%a_%N.err" \
--wrap="srun --label python -m cotracker train-real-video --batch_size 1 \
--num_steps ${NUM_STEPS} --ckpt_path ${scheduler_output} --model_name cotracker_three \
--save_freq 200 --sequence_len 80 --eval_datasets tapvid_stacking tapvid_davis_first \
--traj_per_sample 384 --save_every_n_epoch 15 --evaluate_every_n_epoch 15 --model_stride 4 --dataset_root ${scheduler_data} --num_nodes 4 --real_data_splits 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 \
--num_virtual_tracks 64 --mixed_precision --random_frame_rate \
--restore_ckpt ${scheduler_checkpoint} --lr 0.00005 \
--real_data_filter_sift --validate_at_start --offline_model --limit_samples 10000"
# 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24

