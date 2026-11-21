"""Check the identity, physical configuration and official product of the experiment..

Read-only operations for project integration and testing. Check the results according to the running records on disk..
"""

import json
from pathlib import Path, PurePosixPath
import re
import tomllib

import yaml

from .layout import EXECUTION, NAME, PLAIN_NAME, PURPOSE, experiment_rules
from .naming import contains_english_word, is_configuration_file


RESULT_DIRS = {"artifacts", "reports"}
RUN_DIRS = RESULT_DIRS | {"logs", "metadata", "tmp"}
MANIFESTS = ("metadata/manifest.json", "manifest.json")
STATES = {"running", "succeeded", "failed", "interrupted", "cancelled", "stopped"}


def read_record(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        value = json.loads(text)
    elif path.suffix == ".toml":
        value = tomllib.loads(text)
    else:
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("The record must contain a name section.")
    return value


def relative_file(value):
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts or str(path) != value:
        return None
    return path


def component_path(config, role):
    paths = config.get("component_paths", {})
    if isinstance(paths, dict) and role in paths:
        return paths[role]
    choice = config.get(role)
    return choice.get("name") if isinstance(choice, dict) else choice


def expected_run(manifest, config, relative):
    dataset, model, task = (component_path(config, key) for key in ("dataset", "model", "task"))
    subname = manifest.get("subname")
    role = manifest.get("role")
    run_id = manifest.get("run_id")
    if not all(isinstance(value, str) and re.fullmatch(pattern, value) for value, pattern in (
        (dataset, rf"{NAME}(?:/{NAME})?"), (task, NAME), (subname, PURPOSE), (run_id, EXECUTION),
    )):
        return None
    if model is not None and (not isinstance(model, str) or not re.fullmatch(rf"{NAME}(?:/{NAME})?", model)):
        return None
    if role is not None and (not isinstance(role, str) or not re.fullmatch(PURPOSE, role) or role in RUN_DIRS):
        return None
    if manifest.get("task", task) != task:
        return None
    parts = ["experiment", dataset, model, task, subname, role]
    if relative.parent.name == "executions":
        parts.append("executions")
    return PurePosixPath(*(part for part in [*parts, run_id] if part))


def check_run(directory, relative, rules, fail):
    manifests = [directory / name for name in MANIFESTS if (directory / name).is_file()]
    if len(manifests) != 1:
        fail(relative, "run_manifest", "Use one at a time of execution metadata/manifest.json or manifest.json")
        return
    try:
        manifest = read_record(manifests[0])
    except (OSError, ValueError, yaml.YAMLError) as error:
        fail(relative, "run_manifest", f"The list should be readable:{error}")
        return

    config_path = relative_file(manifest.get("effective_config"))
    if (config_path is None or config_path.suffix not in {".yaml", ".yml", ".json", ".toml"}
            or not rules.matches(str(relative / config_path), False)):
        fail(relative, "effective_config", "Quote the entry into force profile in this execution")
    else:
        try:
            config = read_record(directory / config_path)
        except (OSError, ValueError, yaml.YAMLError) as error:
            fail(relative / config_path, "effective_config", f"Should read the actual effective configuration:{error}")
        else:
            expected = expected_run(manifest, config, relative)
            if expected is None or relative != expected or not rules.matches(str(relative), True):
                fail(relative, "run_identity", f"The execution path should match registered components, research uses and operational identity:{expected or 'Check effective configuration and list'}")
            if manifest.get("configuration") is not None and manifest["configuration"] != config:
                fail(relative / config_path, "config_mismatch", "A valid configuration copy of the list must be consistent with the actual configuration document")

    status = manifest.get("status")
    if not isinstance(status, str) or status not in STATES:
        fail(relative, "run_status", "Inventory records current status of implementation")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or (status == "succeeded" and not outputs):
        fail(relative, "outputs", "List lists the documents in operation by product name; at least one product is successfully run")
        outputs = {}
    declared = set()
    for name, value in outputs.items():
        path = relative_file(value)
        if (path is None or len(path.parts) < 2 or path.parts[0] not in RESULT_DIRS
                or not re.fullmatch(PLAIN_NAME, name) or path.stem != name
                or not (contains_english_word(name) or is_configuration_file(path))
                or not rules.matches(str(relative / path), False)):
            fail(relative, "output_name",
                 f"{name} Should contain full English words and be named alphabetically and should artifacts/ or reports/ File with the same name")
            continue
        declared.add(path)
        if not (directory / path).is_file():
            fail(relative / path, "output_missing", "The products cited in the list must actually exist.")

    for group in RESULT_DIRS:
        for entry in (directory / group).rglob("*"):
            path = PurePosixPath(entry.relative_to(directory).as_posix())
            if any(part.startswith(".") for part in path.parts):
                continue
            if entry.is_file() and path not in declared:
                fail(relative / path, "output_unlisted", "Registered by the person to whom the execution is made, or placed in a separate position according to his actual duties")


def check_experiment(root):
    """Return per-run and per-file failures for the project's experiment tree."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"The project path should be a directory:{root}")
    violations = []
    checked = 0

    def fail(path, rule, expected):
        violations.append({"path": str(path), "rule": rule, "expected": expected})

    def visit(directory):
        nonlocal checked
        relative = PurePosixPath(directory.relative_to(root).as_posix())
        entries = [p for p in directory.iterdir() if not p.name.startswith(".") and p.name != "__pycache__"]
        if (re.fullmatch(EXECUTION, directory.name)
                or any(entry.name in RUN_DIRS | {"manifest.json"} for entry in entries)):
            checked += 1
            check_run(directory, relative, rules, fail)
            return
        for entry in entries:
            if entry.is_dir():
                if not entry.is_symlink():
                    visit(entry)
            elif entry.name not in {"README.md", "recipe.toml"}:
                fail(relative / entry.name, "unowned_file", "Experimental products are subject to a valid execution record.")

    experiments = root / "experiment"
    if experiments.is_dir():
        rules = experiment_rules(root)
        visit(experiments)
    violations.sort(key=lambda item: (item["path"], item["rule"], item["expected"]))
    return {"project": str(root), "passed": not violations, "runs": checked, "violations": violations}
