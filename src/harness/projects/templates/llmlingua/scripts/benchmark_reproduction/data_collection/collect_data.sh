# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd -- "$script_dir/../../.." && pwd)
experiment_root=${LLMLINGUA_EXPERIMENT_ROOT:-"$project_root/experiment"}
run_dir="$experiment_root/meetingbank/gpt_4/data_distillation/word_annotation"

python "$script_dir/label_word.py" --load_prompt_from microsoft/MeetingBank-LLMCompressed \
    --window_size 400 \
    --save_path "$run_dir/annotated.json"

python "$script_dir/filter.py" --load_path "$run_dir/annotated.pt" \
    --save_path "$run_dir/filtered_annotations.pt"
