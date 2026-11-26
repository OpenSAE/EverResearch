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
printf -v scheduler_data '%q' "$DATASET_ROOT"

sbatch --comment=${EXP_NAME} --partition=learn --account=repligen --qos=repligen --time=39:00:00 --gpus-per-node=8 --nodes=4 --ntasks-per-node=8 \
--job-name=${EXP_NAME} --cpus-per-task=10 --signal=USR1@60 --open-mode=append \
--output="${run_directory}/logs/%j_%x_%A_%a_%N.out" \
--error="${run_directory}/logs/%j_%x_%A_%a_%N.err" \
--wrap="srun --label python -m cotracker train-kubric --batch_size 1 \
--num_steps ${NUM_STEPS} --ckpt_path ${scheduler_output} --model_name cotracker_three \
--save_freq 200 --sequence_len 64 --eval_datasets tapvid_davis_first tapvid_stacking \
--traj_per_sample 384 --sliding_window_len 16 --train_datasets kubric \
--save_every_n_epoch 5 --evaluate_every_n_epoch 5 --model_stride 4 --dataset_root ${scheduler_data} --num_nodes 4 \
--num_virtual_tracks 64 --mixed_precision \
--corr_radius 3 --wdecay 0.0005 --linear_layer_for_vis_conf --validate_at_start --add_huber_loss"
