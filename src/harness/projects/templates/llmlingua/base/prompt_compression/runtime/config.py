"""Read the managed compression defaults from the checkout or installed package."""

from functools import lru_cache
from pathlib import Path
from pkgutil import get_data

import yaml


@lru_cache(maxsize=1)
def load_defaults():
    checkout = source_checkout()
    if checkout:
        return yaml.safe_load((checkout / "conf" / "config.yaml").read_text(encoding="utf-8"))
    return yaml.safe_load(get_data("llmlingua", "defaults/config.yaml"))


def source_checkout():
    runtime = Path(__file__).resolve().parent
    if runtime.parent.parent.name == "base":
        return find_checkout(runtime.parent.parent.parent)
    return None


def find_checkout(directory):
    for root in (directory, *directory.parents):
        if (
            (root / "setup.py").is_file()
            and (root / "conf" / "config.yaml").is_file()
            and (root / "base" / "prompt_compression" / "__main__.py").is_file()
        ):
            return root
    return None


def dataset_path(dataset):
    for name, details in load_defaults()["catalogs"]["dataset"].items():
        if details.get("alias") == dataset:
            return name
    return dataset
