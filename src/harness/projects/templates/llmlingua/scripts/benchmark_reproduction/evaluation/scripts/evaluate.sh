# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
data_root=${LLMLINGUA_DATA_ROOT:-"$project_root/data"}
result_root=${LLMLINGUA_EXPERIMENT_ROOT:-"$project_root/experiment"}
cd -- "$project_root/scripts/benchmark_reproduction/evaluation"

python evaluate_meeting_questions.py --load_prompt_from "$result_root/meetingbank_short/llmlingua2/compression_ratio33_meetingbank_test_3qa_pairs_summary_formated.json" \
    --load_key compressed_prompt \
    --model_name_or_path gpt-35-turbo-instruct \
    --save_path "$result_root/meetingbank_short/llmlingua2/gpt35_answer/answer_ratio33_meetingbank_test_3qa_pairs_summary_formated.json"

python evaluate_long_context.py --load_prompt_from "$result_root/longbench/llmlingua2/compression_target2000_longbench_test_single_doc_qa_formated.json" \
    --load_key compressed_prompt \
    --model_name_or_path gpt-35-turbo-instruct \
    --save_path "$result_root/longbench/llmlingua2/gpt35_answer/answer_target2000_longbench_test_single_doc_qa_formated.json"

python evaluate_zero_scrolls.py --load_prompt_from "$result_root/zero_scrolls/llmlingua2/compression_target2000_zero_scrolls_validation.json" \
    --load_key compressed_prompt \
    --model_name_or_path gpt-35-turbo-instruct \
    --save_path "$result_root/zero_scrolls/llmlingua2/gpt35_answer/answer_target2000_zero_scrolls_validation.json"

python evaluate_grade_school_math.py --load_prompt_from "$result_root/gsm8k/llmlingua2/compression_target250_gsm8k_cot_example_all_in_one.json" \
    --load_data_from "$data_root/gsm8k/gsm8k_test.json" \
    --load_key compressed_prompt_list \
    --model_name_or_path gpt-35-turbo-instruct \
    --save_path "$result_root/gsm8k/llmlingua2/gpt35_answer/answer_target250_gsm8k_cot_example_all_in_one.json"
