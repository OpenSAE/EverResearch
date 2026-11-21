# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd -- "$script_dir/../.." && pwd)
experiment_root=${LLMLINGUA_EXPERIMENT_ROOT:-"$project_root/experiment"}
annotation_dir="$experiment_root/jailbreak_pairs/securitylingua/data_distillation/word_annotation"
training_dir="$experiment_root/jailbreak_pairs/microsoft/llmlingua_2_xlm_roberta_large_meetingbank/training/security_distillation"

python "$script_dir/label_word.py" \
    --load_prompt_from liyucheng/jailbreak-pairs \
    --window_size 400 \
    --save_path "$annotation_dir/annotated.pt"

python "$script_dir/filter.py" \
    --load_path "$annotation_dir/annotated.pt" \
    --save_path "$annotation_dir/filtered_annotations.pt"

python "$script_dir/train_roberta.py" \
    --data_path "$annotation_dir/filtered_annotations.pt" \
    --save_path "$training_dir/artifacts/model.pt" \
    --model_name microsoft/llmlingua-2-xlm-roberta-large-meetingbank \
    --num_epoch 5 \
    --run_name meetbank_slingua \
    --wandb_project slingua \
    --wandb_name meetbank_slingua
