"""Locate MathVista configuration, data, and results for its public commands."""

from functools import lru_cache
import os
import re
from pathlib import Path
import tomllib


@lru_cache
def project_root():
    configured = os.environ.get("MATHVISTA_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()

    for parent in (Path.cwd(), *Path(__file__).resolve().parents):
        if (parent / "conf/config.toml").is_file() and (parent / "tasks/scoring").is_dir():
            return parent
    raise SystemExit("Run from a MathVista checkout or set MATHVISTA_PROJECT_ROOT to its path.")


@lru_cache
def configuration():
    with (project_root() / "conf/config.toml").open("rb") as stream:
        return tomllib.load(stream)


def data_root():
    configured = os.environ.get("MATHVISTA_DATA_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (project_root() / configuration()["dataset"]["local_data"]).resolve()


def prepared_context():
    return project_root() / configuration()["dataset"]["prepared_context"]


def dataset_path(split):
    if split == "testmini":
        return "math_vista/mini_test"
    if split == "test":
        return "math_vista/test"
    raise SystemExit("Choose the MathVista split testmini or test, or supply --output_dir.")


def result_directory(split, task, purpose):
    reserved = {"run", "trial", "experiment", "default", "output", "test", "job", "untitled"}
    if purpose in reserved or not re.fullmatch(r"[a-z]+(?:_[a-z]+){0,2}", purpose):
        raise SystemExit("Use up to three lowercase words separated by underscores for --run-purpose.")
    return project_root() / "experiment" / dataset_path(split) / task / purpose / "artifacts"


def standard_file(name):
    if not re.fullmatch(r"[a-z]+(?:_[a-z]+)*\.json", name) or name == "precheck.json":
        raise SystemExit("Use a descriptive JSON filename such as predictions.json.")
    return name
