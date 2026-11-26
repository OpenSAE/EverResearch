#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/instruct_blip_two"
mkdir -p "$work"
if [[ ! -e "$work/output_instructblip2.json" ]]; then
    cp -- assets/history_experiment/published/files/instruct_blip2/output_instruct_blip2_vicuna_13b.json "$work/output_instructblip2.json"
fi

python -m mathvista extract \
    --response_label instructblip2 --output_dir "$work" --output_file output_instructblip2.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_instructblip2.json --output_dir "$work" --output_file output_instructblip2.json --test_split_name testmini --ground_truth_file_path testmini.json
