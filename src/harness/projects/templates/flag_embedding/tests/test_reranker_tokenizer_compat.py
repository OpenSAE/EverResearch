from FlagEmbedding.utils.tokenizer_compat import prepare_for_model_compat


class LegacyTokenizer:
    model_input_names = ["input_ids", "token_type_ids", "attention_mask"]
    truncation_side = "right"

    def __init__(self):
        self.calls = []

    def prepare_for_model(self, first_ids, second_ids, **kwargs):
        self.calls.append((first_ids, second_ids, kwargs))
        return {"input_ids": list(first_ids) + list(second_ids)}


def test_legacy_tokenizer_path_is_preserved():
    tokenizer = LegacyTokenizer()
    actual = prepare_for_model_compat(
        tokenizer,
        [1, 2],
        [3, 4],
        truncation="only_second",
        max_length=8,
        padding=False,
    )

    assert actual["input_ids"] == [1, 2, 3, 4]
    assert len(tokenizer.calls) == 1
    assert tokenizer.calls[0][2]["add_special_tokens"] is True


def test_decoder_only_truncation_respects_tokenizer_side():
    tokenizer = LegacyTokenizer()
    tokenizer.prepare_for_model = None

    right = prepare_for_model_compat(
        tokenizer,
        [1, 2],
        [3, 4, 5],
        truncation="only_second",
        max_length=4,
        padding=False,
        return_attention_mask=False,
        return_token_type_ids=False,
        add_special_tokens=False,
    )
    assert right["input_ids"] == [1, 2, 3, 4]

    tokenizer.truncation_side = "left"
    left = prepare_for_model_compat(
        tokenizer,
        [1, 2],
        [3, 4, 5],
        truncation="only_second",
        max_length=4,
        padding=False,
        return_attention_mask=False,
        return_token_type_ids=False,
        add_special_tokens=False,
    )
    assert left["input_ids"] == [1, 2, 4, 5]
