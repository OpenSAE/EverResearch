#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/mplugowl"
mkdir -p "$work"
if [[ ! -e "$work/output_mplugowl_7b_ft.json" ]]; then
    cp -- assets/history_experiment/published/files/mplugowl/output_mplugowl_7b_ft.json "$work/output_mplugowl_7b_ft.json"
fi

python -m mathvista extract \
    --response_label mplugowl --output_dir "$work" --output_file output_mplugowl_7b_ft.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_mplugowl_7b_ft.json --output_dir "$work" --output_file output_mplugowl_7b_ft.json --test_split_name testmini --ground_truth_file_path testmini.json
