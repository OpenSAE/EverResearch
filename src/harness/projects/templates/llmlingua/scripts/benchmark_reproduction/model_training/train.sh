# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd -- "$script_dir/../../.." && pwd)
experiment_root=${LLMLINGUA_EXPERIMENT_ROOT:-"$project_root/experiment"}
run_dir="$experiment_root/meetingbank/facebookai/xlm_roberta_large/training/meetingbank_distillation"

python "$script_dir/train_roberta.py" \
    --data_path "$experiment_root/meetingbank/gpt_4/data_distillation/word_annotation/filtered_annotations.pt" \
    --save_path "$run_dir/artifacts/model" \
    --log_dir "$run_dir/logs"
