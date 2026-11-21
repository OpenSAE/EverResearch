# ------------------------------------------------------------------------
# RF-DETR
# Copyright (c) 2025 Roboflow. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 [see LICENSE for details]
# ------------------------------------------------------------------------
"""Read named Lightning training recipes from an RF-DETR checkout."""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import yaml

RECIPE_PATH = Path(__file__).resolve().parents[3] / "conf/config.yaml"


def _checkout_recipes() -> Path | None:
    if RECIPE_PATH.is_file():
        return RECIPE_PATH
    current = Path.cwd()
    for directory in (current, *current.parents):
        candidate = directory / "conf/config.yaml"
        if candidate.is_file() and (directory / "base/detector/__init__.py").is_file():
            return candidate
    return None


def load_recipe(name: str, path: Path | None = None) -> dict[str, Any]:
    """Return the Lightning configuration for a named training recipe."""
    source = path or _checkout_recipes()
    if source is None:
        raise FileNotFoundError("Named training recipes are available from an RF-DETR checkout (conf/config.yaml).")
    recipes = cast(dict[str, dict[str, Any]], yaml.safe_load(source.read_text(encoding="utf-8"))["recipes"])
    return recipes[name]


def resolve_recipe_arguments(arguments: Sequence[str]) -> list[str]:
    """Expand named and historical checkout recipes in CLI configuration arguments."""
    recipe_path = _checkout_recipes()
    if recipe_path is None:
        return list(arguments)

    def inline_recipe(value: str) -> str:
        path = Path(value)
        if "/" not in value and "\\" not in value and value.startswith("rfdetr_"):
            name = value
        elif (
            path.suffix == ".yaml"
            and path.parent.name == "configs"
            and (path.parent == Path("configs") or path.parent.resolve() == recipe_path.parents[1] / "configs")
            and not path.exists()
        ):
            name = path.stem
        else:
            return value
        try:
            return json.dumps(load_recipe(name, recipe_path))
        except KeyError:
            return value

    expanded = list(arguments)
    for index, argument in enumerate(arguments):
        if argument in ("--config", "-c") and index + 1 < len(arguments):
            expanded[index + 1] = inline_recipe(arguments[index + 1])
        elif argument.startswith(("--config=", "-c=")):
            option, value = argument.split("=", 1)
            expanded[index] = f"{option}={inline_recipe(value)}"
    return expanded
