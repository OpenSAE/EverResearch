"""Map classifier tokenizers to the padded tensors consumed by compression."""

import torch
from torch.utils.data import Dataset


def token_classifier_family(model_name, tokenizer=None):
    tokens = (getattr(tokenizer, "cls_token", None), getattr(tokenizer, "sep_token", None))
    if tokens == ("[CLS]", "[SEP]"):
        return "bert"
    if tokens == ("<s>", "</s>") and getattr(tokenizer, "mask_token", None) == "<mask>":
        return "xlm_roberta"

    name = model_name.lower()
    if any(
        marker in name
        for marker in ("bert-base-multilingual-cased", "tinybert", "mobilebert")
    ):
        return "bert"
    if any(
        marker in name for marker in ("xlm-roberta-large", "slingua", "securitylingua")
    ):
        return "xlm_roberta"
    raise NotImplementedError(f"Unsupported token-classifier tokenizer: {model_name}")


class TokenClfDataset(Dataset):
    def __init__(
        self,
        texts,
        max_len=512,
        tokenizer=None,
        model_name="bert-base-multilingual-cased",
    ):
        self.len = len(texts)
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.model_name = model_name
        if token_classifier_family(model_name, tokenizer) == "bert":
            self.cls_token = "[CLS]"
            self.sep_token = "[SEP]"
            self.unk_token = "[UNK]"
            self.pad_token = "[PAD]"
            self.mask_token = "[MASK]"
        else:
            self.bos_token = "<s>"
            self.eos_token = "</s>"
            self.sep_token = "</s>"
            self.cls_token = "<s>"
            self.unk_token = "<unk>"
            self.pad_token = "<pad>"
            self.mask_token = "<mask>"

    def __getitem__(self, index):
        text = self.texts[index]
        tokenized_text = self.tokenizer.tokenize(text)

        tokenized_text = (
            [self.cls_token] + tokenized_text + [self.sep_token]
        )  # add special tokens

        if len(tokenized_text) > self.max_len:
            tokenized_text = tokenized_text[: self.max_len]
        else:
            tokenized_text = tokenized_text + [
                self.pad_token for _ in range(self.max_len - len(tokenized_text))
            ]

        attn_mask = [1 if tok != self.pad_token else 0 for tok in tokenized_text]

        ids = self.tokenizer.convert_tokens_to_ids(tokenized_text)

        return {
            "ids": torch.tensor(ids, dtype=torch.long),
            "mask": torch.tensor(attn_mask, dtype=torch.long),
        }

    def __len__(self):
        return self.len
