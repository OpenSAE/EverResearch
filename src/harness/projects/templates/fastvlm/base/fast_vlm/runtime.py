"""Resolve inputs and connect the image reader, checkpoint and generation task."""
import json
import os
from pathlib import Path
from time import perf_counter

from . import SOURCE_ROOT
from .records import save_result


def project_root():
    """Find the source checkout or an explicitly selected wheel workspace."""
    if SOURCE_ROOT is not None:
        return SOURCE_ROOT
    selected = os.environ.get("FASTVLM_WORKSPACE")
    if selected:
        workspace = Path(selected).expanduser().resolve()
        if not workspace.is_dir():
            raise ValueError(f"FASTVLM_WORKSPACE must be an existing directory: {workspace}")
        return workspace
    for directory in (Path.cwd(), *Path.cwd().parents):
        if (directory / "base/fast_vlm/runtime.py").is_file() and (directory / "conf/config.json").is_file():
            return directory
    return None


def defaults():
    config_path = (
        SOURCE_ROOT / "conf/config.json"
        if SOURCE_ROOT is not None
        else Path(__file__).with_name("conf") / "config.json"
    )
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config.pop("catalogs", None)
    return config


def _model_source(value):
    if value is None:
        return None
    path = Path(value).expanduser()
    root = project_root()
    if root is not None and not path.exists():
        legacy = root / "checkpoints"
        old = path.resolve()
        if legacy in old.parents:
            current = root / "data" / old.relative_to(root)
            if current.exists():
                return str(current)
    if path.exists() or path.is_absolute() or value.startswith(("./", "../", "checkpoints/", "data/")):
        return str(path.resolve())
    return value


def resolve_config(overrides):
    config = defaults()
    config.update(overrides)
    if "model_path" not in overrides:
        legacy_model = Path("./llava-v1.5-13b")
        config["model_path"] = str(
            legacy_model.resolve() if legacy_model.is_dir() else (project_root() or Path.cwd()) / config["model_path"]
        )
    config["model_path"] = _model_source(config["model_path"])
    config["model_base"] = _model_source(config["model_base"])
    if config["image_file"] is not None:
        config["image_file"] = str(Path(config["image_file"]).expanduser().resolve())
    return config


def run(config, *, precheck_only=False):
    from .tasks.precheck import prepare_inference

    image_file = Path(config["image_file"])
    if not image_file.is_file():
        raise ValueError(f"Image file does not exist: {image_file}")
    root = project_root()
    if root is None and not precheck_only:
        raise ValueError("Set FASTVLM_WORKSPACE to an existing directory to save inference results.")

    started = perf_counter()
    try:
        image, input_info, resources, report = prepare_inference(config)
    except (OSError, RuntimeError, ValueError) as error:
        if precheck_only:
            raise ValueError(f"Precheck failed: {error}") from error
        manifest = save_result(
            root, config, None, None, precheck_error=str(error),
            precheck_seconds=perf_counter() - started,
        )
        raise ValueError(f"Precheck failed: {error}\nRun manifest: {manifest}") from error
    duration = perf_counter() - started
    if precheck_only:
        return report
    from .tasks.image_prompt import generate_answer

    tokenizer, model, image_processor, device = resources
    answer = generate_answer(image, tokenizer, model, image_processor, config)
    saved_config = {**config, "device": device}
    manifest = save_result(
        root, saved_config, input_info, answer,
        precheck=report, precheck_seconds=duration,
    )
    return answer, manifest
