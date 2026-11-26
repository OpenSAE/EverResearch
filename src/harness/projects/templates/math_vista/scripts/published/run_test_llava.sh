#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/test_llava"
mkdir -p "$work"
: "${MATHVISTA_TEST_LABELS:?Set MATHVISTA_TEST_LABELS to the private test labels file.}"
: "${MATHVISTA_PREDICTIONS:?Set MATHVISTA_PREDICTIONS to the original response JSON.}"
if [[ ! -e "$work/output_llava_llama_2_13b.json" ]]; then
    cp -- "$MATHVISTA_PREDICTIONS" "$work/output_llava_llama_2_13b.json"
fi

python -m mathvista extract \
    --output_dir "$work" --output_file output_llava_llama_2_13b.json --test_split_name test

python -m mathvista score \
    --score_file scores_test_llava_llama_2_13b.json --output_dir "$work" --output_file output_llava_llama_2_13b.json --test_split_name test --ground_truth_file_path "$MATHVISTA_TEST_LABELS"
