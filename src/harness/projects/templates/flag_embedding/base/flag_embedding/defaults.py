"""Load the FlagEmbedding project defaults distributed with the public package."""

import json
from pathlib import Path


def load_evaluation_defaults():
    """Return the shared retrieval defaults consumed by evaluation arguments."""
    module = Path(__file__).resolve()
    configuration = module.with_name("_defaults") / "config.json"
    if not configuration.is_file() and module.parent.parent.name == "base":
        configuration = module.parents[2] / "conf" / "config.json"
    return json.loads(configuration.read_text(encoding="utf-8"))["evaluation"]
