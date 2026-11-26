#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/idefics"
mkdir -p "$work"
if [[ ! -e "$work/output_idefics_9b_instruct.json" ]]; then
    cp -- assets/history_experiment/published/files/idefics/output_idefics_9b_instruct.json "$work/output_idefics_9b_instruct.json"
fi

python -m mathvista extract \
    --response_label idefics --output_dir "$work" --output_file output_idefics_9b_instruct.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_idefics_9b_instruct.json --output_dir "$work" --output_file output_idefics_9b_instruct.json --test_split_name testmini --ground_truth_file_path testmini.json
