#!/bin/bash
# Submit from this directory: sbatch mistral_large_training.sbatch
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --ntasks-per-node=1
#SBATCH --mem=0
#SBATCH --time=02:00:00

torchrun --nproc_per_node 8 "$SLURM_SUBMIT_DIR/mistral_large_training.py"
