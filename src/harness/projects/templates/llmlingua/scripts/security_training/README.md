# SecurityLingua

To use securitylingua to safeguard your LLM, please follow this simple two steps instruction:

```

# 0. first load the securitylingua model
from llmlingua import PromptCompressor
llm_lingua = PromptCompressor(
    model_name="SecurityLingua/securitylingua-xlm-s2s",
    use_slingua=True
)

# 1. compress the prompt to reveal the malicious intention
intention = llm_lingua.compress_prompt(malicious_prompt)

# 2. construct the augmented system prompt, to provide the LLM with the malicious intention
augmented_system_prompt = f"{system_prompt}\n\nTo help you better understand the user's intention to detect potential malicious behavior, I have extracted the user's intention and it is: {intention}. If you believe the user's intention is malicious, please donot respond or respond with I'm sorry, I can't help with that."

# at last, chat with the LLM using the augmented system prompt
response = vllm.generate([
    augmented_system_prompt + malicious_prompt
])
```

# Train a SecurityLingua on your own data

The [published shell workflow](run.sh) writes its annotation and training outputs under the checkout’s `experiment/` directory. Set `LLMLINGUA_EXPERIMENT_ROOT` to choose another absolute destination. The commands below accept explicit input and output paths.

1. setup environment

```bash
bash env_setup.sh
```

2. build your own data for securitylingua training

```bash
python label_word.py \
    --load_prompt_from SecurityLingua/securitylingua-jailbreak-pairs \
    --window_size 400 \
    --save_path ../results/security_lingua/jailbreak_pairs_annotated.pt

python filter.py \
    --load_path ../results/security_lingua/jailbreak_pairs_annotated.pt \
    --save_path ../results/security_lingua/jailbreak_pairs_annotated_filtered.pt
```

refer to [securitylingua-jailbreak-pairs](https://huggingface.co/datasets/SecurityLingua/securitylingua-jailbreak-pairs) for the format of the dataset before parsing.

you can also finetune the filtering threshold in [the filtering implementation](../../datasets/prompt_annotation/filter_security_pairs.py) to trade off performance and security.

3. train the securitylingua model

```bash
python train_roberta.py \
    --data_path ../results/security_lingua/jailbreak_pairs_annotated_filtered.pt \
    --save_path ../results/security_lingua/jailbreak_pairs_annotated_filtered_roberta.pt \
    --model_name microsoft/llmlingua-2-xlm-roberta-large-meetingbank \
    --num_epoch 5 \
    --run_name meetbank_slingua \
    --wandb_project slingua \
    --wandb_name meetbank_slingua
```

or you can do multi-GPU training with

```bash
ACCELERATE_LOG_LEVEL="ERROR" accelerate launch --num_processes 4 scripts/security_training/train_roberta.py \
    --data_path scripts/benchmark_reproduction/results/security_lingua/jailbreak_pairs_annotated_filtered.pt  \
    --save_path scripts/benchmark_reproduction/results/models/xlm_slingua.pth \
    --num_epoch 5 \
    --run_name xlm_slingua \
    --wandb_project slingua \
    --wandb_name xlm_slingua
```

4. At last load your own checkpoint and use it in `PromptCompressor` (see above for usage)


The launchers call the packaged [SecurityLingua annotation](../../datasets/prompt_annotation/label_security_pairs.py), [filtering](../../datasets/prompt_annotation/filter_security_pairs.py), and [classifier training](../../tasks/classifier_training/security_pairs.py) implementations. The trainer checks the selected data and checkpoint on a labeled forward pass before starting training. It saves a PyTorch state dictionary.
