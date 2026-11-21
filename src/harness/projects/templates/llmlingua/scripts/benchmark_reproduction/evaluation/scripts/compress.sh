# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
data_root=${LLMLINGUA_DATA_ROOT:-"$project_root/data"}
result_root=${LLMLINGUA_EXPERIMENT_ROOT:-"$project_root/experiment"}
cd -- "$project_root/scripts/benchmark_reproduction/evaluation"

python compress.py --load_origin_from "$data_root/meetingbank_short/meetingbank_test_3qa_pairs_summary_formated.json" \
    --compression_rate 0.33 \
    --force_tokens "\n,?,!,." \
    --save_path "$result_root/meetingbank_short/llmlingua2/compression_ratio33_meetingbank_test_3qa_pairs_summary_formated.json"

python compress.py --load_origin_from "$data_root/longbench/longbench_test_single_doc_qa_formated.json" \
    --target_token 2000 \
    --force_tokens "\n,?,!,." \
    --save_path "$result_root/longbench/llmlingua2/compression_target2000_longbench_test_single_doc_qa_formated.json"

python compress.py --load_origin_from "$data_root/zero_scrolls/zero_scrolls_validation.json" \
    --target_token 2000 \
    --force_tokens "\n,?,!,." \
    --save_path "$result_root/zero_scrolls/llmlingua2/compression_target2000_zero_scrolls_validation.json"

python compress.py --load_origin_from "$data_root/gsm8k/gsm8k_cot_example_all_in_one.json" \
    --load_key prompt_list \
    --target_token 250 \
    --force_tokens "+,-,*,×,/,÷,=,The answer is,\n" \
    --use_context_level_filter \
    --force_reserve_digit \
    --save_path "$result_root/gsm8k/llmlingua2/compression_target250_gsm8k_cot_example_all_in_one.json"
