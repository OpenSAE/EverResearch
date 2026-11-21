from FlagEmbedding.utils.tokenizer_compat import pad_with_compat


class MappingOnlyTokenizer:
    """Minimal tokenizer double that rejects list-of-mapping inputs."""

    def __init__(self):
        self.received = None
        self.kwargs = None

    def pad(self, encoded_inputs, **kwargs):
        if not isinstance(encoded_inputs, dict):
            raise AttributeError("'list' object has no attribute 'keys'")
        self.received = encoded_inputs
        self.kwargs = kwargs
        return encoded_inputs


def test_pad_with_compat_normalizes_list_of_mappings():
    tokenizer = MappingOnlyTokenizer()
    records = [
        {"input_ids": [101, 10, 102], "attention_mask": [1, 1, 1]},
        {"input_ids": [101, 20, 30, 102], "attention_mask": [1, 1, 1, 1]},
    ]

    result = pad_with_compat(tokenizer, records, padding=True, return_tensors="pt")

    assert result == {
        "input_ids": [[101, 10, 102], [101, 20, 30, 102]],
        "attention_mask": [[1, 1, 1], [1, 1, 1, 1]],
    }
    assert tokenizer.received == result
    assert tokenizer.kwargs == {"padding": True, "return_tensors": "pt"}


def test_pad_with_compat_passes_mapping_inputs_through():
    tokenizer = MappingOnlyTokenizer()
    encoded_inputs = {
        "input_ids": [[101, 10, 102]],
        "attention_mask": [[1, 1, 1]],
    }

    result = pad_with_compat(tokenizer, encoded_inputs, padding=True)

    assert result is encoded_inputs
    assert tokenizer.received is encoded_inputs
