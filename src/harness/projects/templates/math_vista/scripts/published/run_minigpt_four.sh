#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/minigpt_four"
mkdir -p "$work"
if [[ ! -e "$work/output_mathvista_minigpt4_llama2.json" ]]; then
    cp -- assets/history_experiment/published/files/minigpt4/output_minigpt4_llama2.json "$work/output_mathvista_minigpt4_llama2.json"
fi

python -m mathvista extract \
    --response_label minigpt4 --output_dir "$work" --output_file output_mathvista_minigpt4_llama2.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_mathvista_minigpt4_llama2.json --output_dir "$work" --output_file output_mathvista_minigpt4_llama2.json --test_split_name testmini --ground_truth_file_path testmini.json
