"""Resolve the configured checkpoint and tokenizer through the training framework.

The GRPO task calls this adapter before initializing distributed workers.
"""


def load_training_tokenizer(checkpoint):
    from verl.utils import hf_tokenizer
    from verl.utils.fs import copy_local_path_from_hdfs

    resolved = copy_local_path_from_hdfs(checkpoint)
    return resolved, hf_tokenizer(resolved)
