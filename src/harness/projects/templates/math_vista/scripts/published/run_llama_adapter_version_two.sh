#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/llama_adapter_version_two"
mkdir -p "$work"
if [[ ! -e "$work/output_mathvista_llama_adapter_v2.json" ]]; then
    cp -- assets/history_experiment/published/files/llama_adapter_v2/output_llama_adapter_v2.json "$work/output_mathvista_llama_adapter_v2.json"
fi

python -m mathvista extract \
    --response_label llama_adapter --output_dir "$work" --output_file output_mathvista_llama_adapter_v2.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_mathvista_llama_adapter_v2.json --output_dir "$work" --output_file output_mathvista_llama_adapter_v2.json --test_split_name testmini --ground_truth_file_path testmini.json
