"""Check the tokenizer metadata used by the Apple Silicon exporter."""
from fastvlm.tasks.image_prompt.export_vision_encoder import ensure_image_token


def test_export_keeps_the_existing_image_token_id():
    tokens = {"20": {"content": "<image>"}, "25": {"content": "<system>"}}
    config = {"added_tokens_decoder": tokens.copy()}
    assert ensure_image_token(config) == (20, False)
    assert config["added_tokens_decoder"] == tokens


def test_first_export_adds_an_image_token_once():
    template = {"content": "<system>", "special": True}
    config = {"added_tokens_decoder": {"25": template}}
    assert ensure_image_token(config) == (26, True)
    assert ensure_image_token(config) == (26, False)
    assert config["added_tokens_decoder"]["26"] == {"content": "<image>", "special": True}
    assert template["content"] == "<system>"
