#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/llavar"
mkdir -p "$work"
if [[ ! -e "$work/output_llavar.json" ]]; then
    cp -- assets/history_experiment/published/files/llavar/output_llavar.json "$work/output_llavar.json"
fi

python -m mathvista extract \
    --response_label LLaVar --output_dir "$work" --output_file output_llavar.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_llavar.json --output_dir "$work" --output_file output_llavar.json --test_split_name testmini --ground_truth_file_path testmini.json
