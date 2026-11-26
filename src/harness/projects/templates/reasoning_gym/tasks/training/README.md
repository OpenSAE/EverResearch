# Reasoning Gym Model Training

Training codebase for training LLMs using Reasoning Gym procedural dataset generators.

This readme documents:

- Training environment setup and usage example
- Converting training checkpoints to HuggingFace format
- Evaluation setup and usage for eval on RG data
- Evaluation setup and usage for external benchmarks

### Single-device policy training

Run `python main.py train-single --config assets/recipes/workflow_profiles/files/policy_training.yaml --study arithmetic_policy_study` with a CUDA device and the existing TRL and model environment. This command starts with one generated and scored response from each split. Append `--precheck` to stop there. See the [runtime profiles](../../doc/experiment.md) for the measured training and validation workload.

Local evaluation defaults to the original vLLM backend. Specify `--backend transformers` or set `backend: transformers` in the recipe to use Transformers. Both backends load the selected model and score a sample through the `--precheck` mode. The default result location is `experiment/procedural/local_inference/local_evaluation/<study>/`.

### Requirements

We note that we used Python 3.11 and CUDA 11.8 for our experiments. If you are using different versions, you may need to tweak some of the setup.

1. Prepare and activate a Python virtual environment however you prefer.

2. Clone and install Reasoning Gym, and RG-specific training dependencies:

```bash
pip install wheel fire
git clone https://github.com/open-thought/reasoning-gym.git
cd reasoning-gym/
pip install -e .
```

3. Install verl

We used verl at commit hash `c34206925e2a50fd452e474db857b4d488f8602d` with vLLM 0.7.3:
```bash
pip install git+https://github.com/volcengine/verl.git@c34206925e2a50fd452e474db857b4d488f8602d
```

You may alternatively wish to try newer verl versions, which support vLLM 0.8: [Instructions to install verl & vLLM 0.8](https://verl.readthedocs.io/en/latest/README_vllm0.8.html). However, our code does override some verl code, so there may be incompatibilites with newer versions.

4. Install flash attention. The following is a version we found to be compatible with the outlined setup:
```bash
pip install flash-attn==2.7.3 --no-build-isolation
```

5. Log in to HF and W&B:
```bash
huggingface-cli login
wandb login
```

### Usage

Activate the virtual environment you prepared.

Example GRPO training usage, using the config for our inter-domain generalisation experiment trained on Algorithmic problems:

```bash
python -u main.py train --config-path "$PWD/assets/recipes/paper_training/files/configs/inter_generalisation" --config-name algorithmic_qwen_3b
```

Append `+precheck=true` to tokenize one training and one validation row with the selected checkpoint before starting distributed workers.

Set `project_name` and `experiment_name` if logging your runs to W&B. This config assumes a 4 GPU node, but you can configure this too. The following command would be for 2 GPUs, with 1 used for vLLM rollouts:

```bash
python -u main.py train --config-path "$PWD/assets/recipes/paper_training/files/configs/inter_generalisation" --config-name algorithmic_qwen_3b \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    trainer.n_gpus_per_node=2 \
    trainer.project_name=rg-grpo \
    trainer.experiment_name=algorithmic_qwen2.5_3b
```

If you need to use only a subset of the GPUs on the machine, set the `CUDA_VISIBLE_DEVICES` environment variable, for example:

```bash
export CUDA_VISIBLE_DEVICES=0,1
```

See `nvidia-smi` output for your system GPU IDs. `n_gpus_per_node` should be set to the total number of GPUs you are using. `tensor_model_parallel_size` should be set to the number you wish to use for vLLM rollouts.

You can change all configuration options by either modifying the config YAML (in this case, `assets/recipes/paper_training/files/configs/inter_generalisation/algorithmic_qwen_3b.yaml`) or providing them as args to the Python script.


# Exporting from FSDP checkpoint to HF model checkpoint

After training your model the weights are saved across as a sharded checkpoints across several files. To faciliate simple evaluation of your trained model you may want to convert this into a HF model checkpoint. We have added a utility script to convert your sharded checkpoint into a hf checkpoint.

To run this script. Run the following from the checkout root

```bash
python scripts/checkpoints/load_fsdp_to_hf.py /path/to/fsdp/checkpoint/global_step_num/actor /path/to/hugginface/checkpoint/global_step_num/actor/huggingface saved_model_name
```

For example

```bash
python scripts/checkpoints/load_fsdp_to_hf.py checkpoints/rg-test/intra_reasoning_algorithmic_qwen_3b_composite/global_step_400/actor/ checkpoints/rg-test/intra_reasoning_algorithmic_qwen_3b_composite/global_step_400/actor/huggingface qwen3b
```

# Run evaluations

From here you may to run evaluations of your trained model. In the `tasks/local_evaluation` directory there is a script `evaluate_model.py` which you csn run to evaluate your trained model on a specific dataset. You specify evaluation parameters in a yaml file. This evaluation can point to either a local or remote model. For example the configuration file `assets/recipes/paper_training/files/evaluations/intra_generalisation/eval_algorithmic_composite.yaml` specifies the path to a local model which is stored as a hugginface checkpoint at `training/utils/qwen3b_500` (note that you have to convert to fsdp checkpoint to hf checkpoint for evaluation script to work as shown in the previous step).

## Run the script

```bash
export VLLM_ATTENTION_BACKEND=XFORMERS
```

Run from the checkout root:

```bash
python main.py evaluate-local --config path-to-yaml
```

For example:

```bash
python main.py evaluate-local --config assets/recipes/paper_training/files/evaluations/intra_generalisation/eval_algorithmic_composite.yaml
```

## External benchmark evaluations

We additionally evaluate some models on external benchmarks using the [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) from Eleuther AI.


### Math benchmarks

We utilise the `llama` branch for the Llama 3 MATH and GSM8K evaluation configurations it provides, for the fairest possible comparison against Meta's original Llama 3 model.

```bash
git clone https://github.com/EleutherAI/lm-evaluation-harness.git
cd lm-evaluation-harness
git checkout llama
pip install -e .
```

1. For our **Llama 3 3B RG-Math** model, we evaluate both the original model and ours by directly using the Llama 3 configs provided by LMEH:
    ```bash
    # tasks used: llama_math, gsm8k_cot_llama
    lm_eval --model vllm --model_args pretrained=/path/to/model --tasks llama_math --batch_size auto --output_path results/ --apply_chat_template --fewshot_as_multiturn
    ```

2. For our **Qwen 2.5 3B RG-Math** model, we evaluate using a tweaked version of the same task configs. The system prompt used in RL is also used in evaluation for the RG-Math model. The original Qwen 2.5 model was tested with the same system prompt, but performed worse than with the standard CoT prompt, so the final evaluation score utilised the standard prompt.
    ```bash
    # tasks used: llama_math (edited, see below), gsm8k_cot_rg
    lm_eval --model vllm --model_args pretrained=/path/to/model --tasks llama_math --batch_size auto --output_path results/ --apply_chat_template
    ```

The RG-specific task configs for LMEH are contained in `training/evaluations/lmeh/` in this repository. To run the `llama_math` eval, replace `llama_math_algebra` in the relevant LMEH tasks directory with the RG one provided.

### MMLU Pro

For MMLU Pro, we use the `mmlu_pro` task from LMEH. To run the evaluation, you can use the following command:

```bash
lm_eval --model vllm --model_args pretrained=/path/to/model --tasks mmlu_pro --batch_size auto --output_path results/ --apply_chat_template --fewshot_as_multiturn
```
