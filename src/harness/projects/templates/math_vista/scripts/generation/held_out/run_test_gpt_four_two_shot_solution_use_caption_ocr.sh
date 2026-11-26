#!/usr/bin/env bash
# Reproduce a published MathVista evaluation recipe from the project environment.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$root"
work="$root/tmp/legacy_reproduction/test_gpt_four_two_shot_solution_use_caption_ocr"
mkdir -p "$work"
: "${MATHVISTA_TEST_LABELS:?Set MATHVISTA_TEST_LABELS to the private test labels file.}"

python -m mathvista generate \
    --model gpt-4-0613 --shot_num 2 --shot_type solution --use_caption --use_ocr --caption_file assets/prepared_data/visual_context/files/captions_bard.json --ocr_file assets/prepared_data/visual_context/files/ocrs_easyocr.json --output_dir "$work" --output_file output_test_gpt4_2shot_solution_use_caption_ocr.json --test_split_name test

python -m mathvista extract \
    --output_dir "$work" --output_file output_test_gpt4_2shot_solution_use_caption_ocr.json --test_split_name test

python -m mathvista score \
    --score_file scores_test_gpt4_2shot_solution_use_caption_ocr.json --output_dir "$work" --output_file output_test_gpt4_2shot_solution_use_caption_ocr.json --test_split_name test --ground_truth_file_path "$MATHVISTA_TEST_LABELS"
