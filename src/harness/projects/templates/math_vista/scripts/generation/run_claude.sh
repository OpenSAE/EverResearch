#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/claude"
mkdir -p "$work"

python -m mathvista generate \
    --model claude-2 --output_dir "$work" --output_file output_claude.json --test_split_name testmini

python -m mathvista extract \
    --output_dir "$work" --output_file output_claude.json --test_split_name testmini

python -m mathvista score \
    --score_file scores_claude.json --output_dir "$work" --output_file output_claude.json --test_split_name testmini --ground_truth_file_path testmini.json
