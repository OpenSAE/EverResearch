#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/llava"
mkdir -p "$work"
if [[ ! -e "$work/output_llava_llama_2_13b.json" ]]; then
    cp -- assets/history_experiment/published/files/llava/output_llava_llama_2_13b.json "$work/output_llava_llama_2_13b.json"
fi

python -m mathvista extract \
    --response_label llava_llama_2_13b --output_dir "$work" --output_file output_llava_llama_2_13b.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_llava_llama_2_13b.json --output_dir "$work" --output_file output_llava_llama_2_13b.json --test_split_name testmini --ground_truth_file_path testmini.json
