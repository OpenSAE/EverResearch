# Local workflow verification

The CPU checks used PyTorch 2.9.1, the two available ClimbMix shards,
the locally prepared 512-token BPE, and the existing one-layer NanoChat
checkpoints. The GPU benchmark and tests used the host CUDA 12.8 PyTorch 2.10
environment on an RTX 5090. These runs check operability on small inputs.

| Workflow | Verified result |
| --- | --- |
| ClimbMix preparation | The download entry recognized both existing files. Train and validation each yielded a real first row group of 1,024 documents. |
| Conversational inputs | Read examples from both ARC subsets and all their splits, MMLU auxiliary train, validation, dev, and test, both GSM8K subsets and splits, HumanEval test, and SmolTalk train and test. |
| Tokenization | Trained and saved a 512-token BPE on a bounded ClimbMix input and evaluated compression through the original entry point. |
| Base training | Ran one optimization step from scratch. Reloaded its checkpoint through base evaluation. Validation BPB was 4.499515, matching the retained run with the same configuration. |
| Base evaluation | Loaded the existing longer-context base checkpoint and completed BPB, samples, and one scored example per CORE task. Read back the CORE CSV. |
| SFT | Loaded a base checkpoint and its optimizer, ran one bounded SFT step, and saved model, metadata, and optimizer files. |
| RL | Loaded SFT weights, sampled from GSM8K, evaluated pass@k, took one optimizer step, and saved and reloaded the RL checkpoint. |
| Chat evaluation | Read RL weights and exercised both ARC subsets, MMLU, GSM8K, and HumanEval with one problem each. |
| Inference | Verified single-prompt SFT generation on CPU and the single-batch CUDA inference benchmark. |
| Packaging | Built an sdist and a wheel. Checked public imports and ran a precheck from a separate directory with the wheel installed. |

## Start with a fresh cache

Use the [environment guide](environment/README.md) to install the CPU
environment and download the real ClimbMix shards. Then run these commands
from the project root.

```sh
export OMP_NUM_THREADS=2 TORCHINDUCTOR_COMPILE_THREADS=1
python -m scripts.tok_train --max-chars 100000 --vocab-size 512
python -m nanochat run --subname portable_smoke base_train \
  --device-type cpu --depth 1 --aspect-ratio 32 --head-dim 32 \
  --max-seq-len 16 --window-pattern L --num-iterations 1 \
  --device-batch-size 1 --total-batch-size 16 --eval-tokens 16 \
  --core-metric-every -1 --sample-every -1 --model-tag portable_smoke
python -m scripts.base_eval --device-type cpu --model-tag portable_smoke \
  --step 1 --eval bpb --device-batch-size 1 --split-tokens 64
```

The managed command writes a precheck report, effective configuration, and
console log beneath `experiment/climbmix_corpus/transformer/base_training/`.
The evaluation reopens the checkpoint written in `NANOCHAT_BASE_DIR`.

## Reproduce small runs with existing checkpoints

Set the data paths as described in the [environment guide](environment/README.md).
Set `NANOCHAT_BASE_DIR` to a writable working copy of the required tokenizer and
checkpoints. The names below refer to the local acceptance checkpoints. Supply
your own tag and architecture when using another checkpoint. The checks take
seconds to a few minutes with local inputs, depending on compile caches and hardware.

```sh
# Train a new tokenizer in a separate writable NANOCHAT_BASE_DIR.
python -m scripts.tok_train --max-chars 100000 --vocab-size 512
python -m scripts.tok_eval

# Use the working copy with the existing checkpoints for the rest.
python -m nanochat precheck
python -m scripts.base_train --device-type cpu --depth 1 --aspect-ratio 32 \
  --head-dim 32 --max-seq-len 16 --window-pattern L --num-iterations 1 \
  --device-batch-size 1 --total-batch-size 16 --eval-tokens 16 \
  --core-metric-every -1 --sample-every -1 --model-tag migration

python -m scripts.base_eval --device-type cpu --model-tag core_adoption \
  --eval core,bpb,sample --device-batch-size 1 --split-tokens 2048 --max-per-task 1

python -m nanochat precheck --task fine_tuning --model-tag chat_adoption
python -m scripts.chat_sft --device-type cpu --model-tag chat_adoption \
  --num-iterations 2 --device-batch-size 1 --total-batch-size 512 \
  --eval-tokens 512 --chatcore-every -1 --mmlu-epochs 1 --gsm8k-epochs 1

python -m nanochat precheck --task fine_tuning --rl --model-tag chat_adoption
python -m scripts.chat_rl --device-type cpu --model-tag chat_adoption \
  --num-iterations 1 --device-batch-size 2 --examples-per-step 1 \
  --num-samples 2 --max-new-tokens 2 --eval-examples 1

python -m nanochat precheck --task evaluation --source rl --model-tag chat_adoption
python -m scripts.chat_eval --device-type cpu --source rl --model-tag chat_adoption \
  --max-problems 1 --max-new-tokens 1 --batch-size 1
python -m scripts.chat_cli --device-type cpu --source sft --model-tag chat_adoption -p Hello

# Run in the CUDA environment.
python -m scripts.infer_bench --source base --model-tag core_adoption \
  --prompt-tokens 8 --decode-tokens 2 --batch-sizes 1
```

The application writes tokenizer files under `tokenizer/`, model artifacts under
`base_checkpoints/`, `chatsft_checkpoints/` and `chatrl_checkpoints/`, and the
CORE scores under `base_eval/` inside `NANOCHAT_BASE_DIR`. These paths are also
used for historical readback. The shell recipes in [scripts](../scripts/) provide
the original full training options and their hardware requirements.

## Managed execution records

Use the same command-line arguments with the EverResearch launcher. It checks
real inputs before launching the selected command and writes the effective
launch configuration, precheck, and command output under `experiment/`.

```sh
python -m nanochat run --subname validation base_eval --device-type cpu \
  --model-tag core_adoption --eval bpb --device-batch-size 1 --split-tokens 2048
rh projects experiment check .
```

The workflow names are `tokenizer_train`, `tokenizer_eval`, `base_train`,
`base_eval`, `supervised`, `reinforcement`, `chat_eval`, `chat`, and
`inference_benchmark`. For managed chat, supply a prompt. The original chat
command supports interactive sessions. Read the status in
`metadata/manifest.json` and the work output in `reports/console.txt` within the
printed run directory. Tokenizer files, checkpoints, and CORE CSVs use the
normal `NANOCHAT_BASE_DIR` storage described above.
