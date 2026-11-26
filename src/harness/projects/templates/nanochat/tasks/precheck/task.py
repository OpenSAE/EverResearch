"""Bounded input and model checks using the production readers and transformer."""

import torch

from nanochat.checkpoint_manager import load_model
from nanochat.climbmix.data_loader import tokenizing_distributed_data_loader_bos_bestfit
from nanochat.climbmix.dataset import list_parquet_files, parquets_iter_batched
from nanochat.tokenization.tokenizer import get_tokenizer
from nanochat.transformer.network import GPT, GPTConfig
from tasks.conversation.arc import ARC
from tasks.conversation.grade_school_math import GSM8K
from tasks.conversation.human_evaluation import HumanEval
from tasks.conversation.knowledge_questions import MMLU
from tasks.conversation.small_talk import SmolTalk


def check_corpus():
    paths = list_parquet_files(warn_on_legacy=True)
    if len(paths) < 2:
        raise ValueError("ClimbMix needs at least one training shard and one validation shard")
    return {split: len(next(parquets_iter_batched(split))) for split in ("train", "val")}


@torch.no_grad()
def check_model_batch(model, inputs, targets=None):
    result = model(inputs, targets)
    if not torch.isfinite(result).all().item():
        raise ValueError("The model produced non-finite values on the precheck batch")
    return list(result.shape)


def check(args):
    result = {"task": args.task, "device": args.device, "samples_checked": 0}
    workflow = getattr(args, "workflow", None)
    if workflow == "inference_benchmark" and torch.device(args.device).type != "cuda":
        raise ValueError("The inference benchmark requires a CUDA GPU")
    if args.task in {"base_training", "tokenization"}:
        result["corpus"] = check_corpus()
        result["samples_checked"] += sum(result["corpus"].values())
    if args.task == "tokenization":
        if workflow == "tokenizer_eval":
            result["vocab_size"] = get_tokenizer().get_vocab_size()
        return result

    device = torch.device(args.device)
    if args.task == "base_training" and args.source is None:
        tokenizer = get_tokenizer()
        arch = getattr(args, "architecture", None)
        config = GPTConfig(sequence_len=16, vocab_size=tokenizer.get_vocab_size(),
                           n_layer=1, n_head=1, n_kv_head=1, n_embd=32, window_pattern="L")
        if arch is not None:
            if min(arch.depth, arch.aspect_ratio, arch.head_dim, arch.max_seq_len) < 1:
                raise ValueError("Model dimensions and sequence length must be positive")
            width = arch.depth * arch.aspect_ratio
            heads = (width + arch.head_dim - 1) // arch.head_dim
            config = GPTConfig(sequence_len=arch.max_seq_len, vocab_size=tokenizer.get_vocab_size(),
                               n_layer=arch.depth, n_head=heads, n_kv_head=heads,
                               n_embd=heads * arch.head_dim, window_pattern=arch.window_pattern)
        with torch.device(device):
            model = GPT(config)
        model.init_weights()
        result["source"] = "scratch"
    else:
        source = args.source or ("sft" if args.task == "fine_tuning" and args.rl else "base")
        model, tokenizer, meta = load_model(source, device, phase="eval",
                                            model_tag=args.model_tag, step=args.step)
        result.update(source=source, step=meta["step"])

    if args.task == "base_training" or (args.task == "evaluation" and result["source"] == "base"):
        result["splits"] = {}
        sequence_len = min(16, model.config.sequence_len)
        for split in ("train", "val"):
            loader = tokenizing_distributed_data_loader_bos_bestfit(tokenizer, 1, sequence_len, split, device=device)
            inputs, targets = next(loader)
            result["splits"][split] = check_model_batch(model, inputs, targets)
            result["samples_checked"] += inputs.size(0)
        return result

    cases = {}
    if args.task == "fine_tuning":
        cases = {
            "gsm_train": (GSM8K, {"subset": "main", "split": "train"}),
            "gsm_test": (GSM8K, {"subset": "main", "split": "test"}),
        }
        if not args.rl:
            cases.update(
                smol_train=(SmolTalk, {"split": "train"}),
                smol_test=(SmolTalk, {"split": "test"}),
                mmlu_train=(MMLU, {"subset": "all", "split": "auxiliary_train"}),
                mmlu_test=(MMLU, {"subset": "all", "split": "test"}),
            )
    elif args.task == "evaluation":
        cases = {
            "arc_easy": (ARC, {"subset": "ARC-Easy", "split": "test"}),
            "arc_challenge": (ARC, {"subset": "ARC-Challenge", "split": "test"}),
            "mmlu_test": (MMLU, {"subset": "all", "split": "test"}),
            "gsm_test": (GSM8K, {"subset": "main", "split": "test"}),
            "human_eval": (HumanEval, {}),
        }

    result["samples"] = {}
    for name, (reader, kwargs) in cases.items():
        dataset = reader(**kwargs)
        tokens, _ = tokenizer.render_conversation(dataset[0], max_tokens=model.config.sequence_len)
        inputs = torch.tensor([tokens], device=device)
        result["samples"][name] = {"rows": len(dataset), "shape": check_model_batch(model, inputs)}
        result["samples_checked"] += 1
    if args.task == "inference":
        from tasks.inference.engine import Engine

        prompt = tokenizer(getattr(args, "prompt", "Hello"), prepend="<|bos|>")
        completions, _ = Engine(model, tokenizer).generate_batch(prompt, num_samples=1, max_tokens=1, temperature=0)
        result["generated_tokens"] = len(completions[0]) - len(prompt)
        result["samples_checked"] += 1
    return result
