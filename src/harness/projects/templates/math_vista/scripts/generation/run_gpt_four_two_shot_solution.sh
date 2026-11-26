#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/gpt_four_two_shot_solution"
mkdir -p "$work"

python -m mathvista generate \
    --model gpt-4-0613 --shot_num 2 --shot_type solution --output_dir "$work" --output_file output_gpt4_2shot_solution.json --test_split_name testmini

python -m mathvista extract \
    --output_dir "$work" --output_file output_gpt4_2shot_solution.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_gpt4_2shot_solution.json --output_dir "$work" --output_file output_gpt4_2shot_solution.json --test_split_name testmini --ground_truth_file_path testmini.json
