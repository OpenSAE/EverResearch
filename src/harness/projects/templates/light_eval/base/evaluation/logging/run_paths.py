"""Locate CLI evaluation studies and allocate independent Inspect AI runs."""

import hashlib
import json
import os
import re
import tempfile
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

import yaml


DEFAULT_EXPERIMENT_NAME = "benchmark_evaluation"


def _checkout_root() -> Path | None:
    package_path = Path(__file__).resolve().parents[1]
    checkout = package_path.parent.parent
    if package_path.parent.name == "base" and (checkout / "pyproject.toml").is_file():
        return checkout
    return None


@lru_cache(maxsize=1)
def _study_names() -> dict[str, dict[str, str]]:
    """Map public dataset, model, and task identifiers to stable study names."""
    checkout = _checkout_root()
    directory = checkout / "conf" if checkout else Path(__file__).resolve().parents[1] / "study_configuration"
    config = directory / "config.yaml"
    with config.open(encoding="utf-8") as stream:
        catalogs = yaml.safe_load(stream)["catalogs"]
    return {role: {identifier: name for name, identifier in entries.items()} for role, entries in catalogs.items()}


def experiment_root() -> Path:
    """Use an explicit workspace, the source checkout, or the installed CLI's working directory."""
    if workspace := os.environ.get("LIGHTEVAL_WORKSPACE"):
        return Path(workspace).expanduser().resolve() / "experiment"
    return (_checkout_root() or Path.cwd()) / "experiment"


def validate_experiment_name(name: str) -> None:
    """Require a short name that describes the evaluation's purpose."""
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", name) or re.fullmatch(
        r"run|eval|evaluation|experiment|job|trial|test|default|output|untitled", name
    ):
        raise ValueError("Use one to three words describing the evaluation, such as 'answer_accuracy'.")


def _selection_directory(identifiers: list[str], names: dict[str, str], kind: str) -> str:
    unique_identifiers = sorted(set(identifiers))
    if len(unique_identifiers) == 1:
        identifier = unique_identifiers[0]
        if identifier in names:
            return names[identifier]
        if len(identifier) <= 140 and re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", identifier):
            if identifier not in names.values():
                return identifier

    words = [
        names.get(identifier, re.sub(r"[^a-z0-9]+", "_", identifier.lower()).strip("_"))
        for identifier in unique_identifiers
    ]
    label = "_and_".join(word for word in words if word)[:140].rstrip("_") or kind
    # Preserve the identity of selections whose readable labels can coincide.
    digest = hashlib.sha256(json.dumps(unique_identifiers).encode()).hexdigest()[:16]
    return f"{label}__{digest}"


def _legacy_selection_directory(identifiers: list[str], kind: str) -> str:
    unique_identifiers = sorted(set(identifiers))
    if len(unique_identifiers) == 1:
        identifier = unique_identifiers[0]
        # Inspect interprets percent escapes in file URLs. Use a distinct escape
        # character so encoded slashes remain part of a single directory name.
        escaped = quote(identifier, safe="").replace("~", "~7E").replace("%", "~")
        if escaped not in ("", ".", "..") and len(escaped) <= 180:
            return escaped
    digest = hashlib.sha256(json.dumps(unique_identifiers).encode()).hexdigest()[:16]
    return f"{kind}_{digest}"


def study_directory(datasets: list[str], models: list[str], tasks: list[str], experiment_name: str) -> Path:
    """Locate a study from the dataset, model, task, and research purpose."""
    validate_experiment_name(experiment_name)
    names = _study_names()
    dataset_directory = experiment_root() / _selection_directory(datasets, names["dataset"], "datasets")
    if models:
        dataset_directory /= _selection_directory(models, names["model"], "models")
    task_names = [re.sub(r"\|[0-9]+$", "", task) for task in tasks]
    return dataset_directory / _selection_directory(task_names, names["task"], "tasks") / experiment_name


def previous_study_directory(study: Path, *, has_model: bool) -> Path:
    """Locate a study written before names were expanded and executions were recorded."""
    root = experiment_root()
    components = list(study.relative_to(root).parts)
    if components[0] == "grade_school_math":
        components[0] = "gsm8k"
    if has_model and components[1] == "gpt2_transformer":
        components[1] = "gpt2"
    return root.joinpath(*components)


def legacy_study_directory(datasets: list[str], models: list[str], tasks: list[str], experiment_name: str) -> Path:
    """Find studies saved with the previous identifier-escape layout."""
    validate_experiment_name(experiment_name)
    directory = experiment_root() / _legacy_selection_directory(datasets, "datasets")
    if models:
        directory /= _legacy_selection_directory(models, "models")
    return directory / _legacy_selection_directory(tasks, "tasks") / experiment_name


def allocate_inspect_log_dir(datasets: list[str], models: list[str], tasks: list[str], experiment_name: str) -> Path:
    """Allocate an Inspect log directory inside the study's run storage."""
    runs = study_directory(datasets, models, tasks, experiment_name) / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="evaluation_", dir=runs))
