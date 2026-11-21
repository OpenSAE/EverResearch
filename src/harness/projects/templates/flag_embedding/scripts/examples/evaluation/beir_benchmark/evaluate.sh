#!/usr/bin/env bash
# Evaluate the published BEIR recipe and save one experiment per dataset.
set -euo pipefail

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf 'Usage: bash %s [DATASET EXPERIMENT_NAME [evaluation options]]\n' "$0"
    printf 'With no arguments, run FiQA, ArguAna and CQADupStack as retrieval_and_rerank.\n'
    exit 0
fi

datasets=(fiqa arguana cqadupstack)
experiment_name=retrieval_and_rerank
if (( $# > 0 )); then
    if (( $# < 2 )); then
        printf 'Expected DATASET and EXPERIMENT_NAME. Use --help for usage.\n' >&2
        exit 2
    fi
    datasets=("$1")
    experiment_name=$2
    shift 2
fi

if [[ ! $experiment_name =~ ^[a-z]+(_[a-z]+){0,2}$ || $experiment_name =~ ^(run|test|default)$ ]]; then
    printf 'Describe the experiment with one to three lowercase words, such as retrieval_and_rerank.\n' >&2
    exit 2
fi

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
hub_cache=${HF_HUB_CACHE:-${HF_HOME:-$HOME/.cache/huggingface}/hub}
dataset_dir=${BEIR_DATASET_DIR:-$hub_cache/beir/input}
embedder=${BEIR_EMBEDDER:-BAAI/bge-large-en-v1.5}
embedder=${embedder%/}
model_name=${embedder##*/}
if [[ ! $model_name =~ ^[[:alnum:]][[:alnum:]_.-]*$ ]]; then
    printf 'The embedder name must start with a letter or digit and may contain dots, underscores, and hyphens.\n' >&2
    exit 2
fi

model_cache=()
if [[ -n ${HF_MODEL_CACHE:-} ]]; then
    model_cache=(--cache_dir "$HF_MODEL_CACHE")
fi

for dataset in "${datasets[@]}"; do
    if [[ ! $dataset =~ ^[[:alnum:]][[:alnum:]_.-]*$ ]]; then
        printf 'The dataset name must start with a letter or digit and may contain dots, underscores, and hyphens.\n' >&2
        exit 2
    fi
    output_dir="$project_root/experiment/$dataset/$model_name/retrieval/$experiment_name"
    python -m FlagEmbedding.evaluation.beir \
        --splits test dev --search_top_k 1000 --rerank_top_k 100 \
        --k_values 10 100 --eval_metrics ndcg_at_10 recall_at_100 \
        --ignore_identical_ids True --reranker_max_length 1024 \
        "${model_cache[@]}" "$@" \
        --eval_name beir --dataset_dir "$dataset_dir" --dataset_names "$dataset" \
        --cache_path "${BEIR_DATASET_CACHE:-$hub_cache}" \
        --embedder_name_or_path "$embedder" \
        --reranker_name_or_path "${BEIR_RERANKER:-BAAI/bge-reranker-v2-m3}" \
        --corpus_embd_save_dir "$output_dir/corpus_embd" \
        --output_dir "$output_dir/search_results" \
        --eval_output_method markdown --eval_output_path "$output_dir/beir_eval_results.md"
done
