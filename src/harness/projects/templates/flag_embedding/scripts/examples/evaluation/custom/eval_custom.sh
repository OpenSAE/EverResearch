#!/usr/bin/env bash
# Evaluate local retrieval data and place the results in the checkout's experiment directory.
set -euo pipefail

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf 'Usage: bash %s DATASET_NAME DATASET_DIR EMBEDDER EXPERIMENT_NAME [evaluation options]\n' "$0"
    exit 0
fi

if (( $# < 4 )); then
    printf 'Expected DATASET_NAME DATASET_DIR EMBEDDER EXPERIMENT_NAME. Use --help for usage.\n' >&2
    exit 2
fi

dataset_name=$1
dataset_dir=$2
embedder=${3%/}
experiment_name=$4
shift 4

if [[ ! $experiment_name =~ ^[a-z]+(_[a-z]+){0,2}$ || $experiment_name =~ ^(run|test|default)$ ]]; then
    printf 'Describe the experiment with one to three lowercase words, such as dense_retrieval.\n' >&2
    exit 2
fi

model_name=${embedder##*/}
if [[ ! $dataset_name =~ ^[[:alnum:]][[:alnum:]_.-]*$ || ! $model_name =~ ^[[:alnum:]][[:alnum:]_.-]*$ ]]; then
    printf 'Dataset and model names must start with a letter or digit and may contain dots, underscores, and hyphens.\n' >&2
    exit 2
fi

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
output_dir="$project_root/experiment/$dataset_name/$model_name/retrieval/$experiment_name"

exec python -m FlagEmbedding.evaluation.custom \
    "$@" \
    --eval_name "$dataset_name" \
    --dataset_dir "$dataset_dir" \
    --embedder_name_or_path "$embedder" \
    --output_dir "$output_dir/search_results" \
    --eval_output_method json \
    --eval_output_path "$output_dir/eval_results.json"
