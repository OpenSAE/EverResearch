"""Check the catalogue of scientific projects, document attribution, configuration depth and experimental path.

Read-only check of project trees for maintenance processes and local commands, and determine layout using statements and directory names.
"""

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

import yaml

from .naming import is_configuration_file, path_name_violations, project_name_valid


NAME = r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*"
PLAIN_NAME = r"[a-z]+(?:_[a-z]+)*"
PURPOSE = (r"(?!(?:run|trial|experiment|default|output|test|job|untitled)(?:_?\d+)?(?:/|$))"
           r"[a-z]+(?:_[a-z]+){0,2}")
EXECUTION = r"[0-9]{8}T[0-9]{6}(?:\.[0-9]+)?Z?-[a-z0-9-]+"
CODE = rf"(?:{NAME}|__[a-z]+__)\.(?:py|pyi|sh|R|r|jl|rs|c|cc|cpp|h|hpp|cu|cuh|js|ts|m|ipynb)"
SCRIPT = rf"{NAME}\.(?:py|sh|R|r|jl|js|ts|m|ipynb|sbatch)"
CONFIG = rf"{NAME}\.(?:yaml|yml|toml|json)"
MARKDOWN = rf"(?:README|{NAME})\.md"
DOC_PAGES = (
    r"README|agents|base|datasets|models|tasks|conf|experiment|data|scripts|tests|assets"
    r"|third_party|tmp|maintenance"
)
PAYLOAD = r"[A-Za-z0-9][A-Za-z0-9_.+-]*"
RESOURCE = rf"(?![^/]+\.(?:py|sh|R|r|jl|js|ts|m|ipynb|sbatch)$){PAYLOAD}"
ROOT_FILES = (
    r"README\.md|AGENTS\.md|LICENSE(?:\.txt|\.md)?|NOTICE(?:\.txt|\.md)?|CITATION\.cff"
    r"|CHANGELOG\.md|CONTRIBUTING\.md|pyproject\.toml|setup\.(?:py|cfg)"
    r"|requirements(?:_[a-z0-9]+)?\.txt|main\.py|Makefile|CMakeLists\.txt|Cargo\.toml"
    r"|package\.json|uv\.lock|poetry\.lock|pytest\.ini"
)
COMPONENTS = {"dataset": "datasets", "model": "models", "task": "tasks"}


@dataclass(frozen=True)
class Rules:
    directories: tuple[str, ...]
    files: tuple[str, ...]

    def matches(self, path, is_directory):
        patterns = self.directories if is_directory else self.files
        return any(re.fullmatch(pattern, path) for pattern in patterns)


def code_tree(prefix, branches):
    return Rules((prefix, branches),
                 (rf"{prefix}/(?:{CODE}|README\.md|py\.typed)",
                  rf"{branches}/(?:{CODE}|README\.md|py\.typed)"))


def component(root, root_modules):
    branch = rf"{root}(?:/{NAME}){{1,2}}"
    return Rules(
        (root, branch),
        (rf"{root}/(?:README\.md|__init__\.py|(?:{root_modules})\.py)",
         rf"{branch}/(?:{CODE}|README\.md)"),
    )


RULES = {
    "base": code_tree("base", rf"base(?:/{NAME})+"),
    "datasets": component("datasets", "plugins"),
    "models": component("models", "plugins|build"),
    "tasks": component("tasks", "plugins"),
    "conf": Rules((r"conf(?:/[A-Za-z][A-Za-z0-9_]*){0,2}",),
                  (rf"conf(?:/[A-Za-z][A-Za-z0-9_]*){{0,2}}/{CONFIG}",)),
    "doc": Rules(
        ("doc", rf"doc/(?:code|knowledge|environment)(?:/{NAME})*", r"doc/experiment",
         rf"doc/experiment/{NAME}", rf"doc/code/{NAME}/source(?:/[^/]+)*"),
        (rf"doc/(?:{DOC_PAGES})\.md", rf"doc/(?:code|knowledge|environment)(?:/{NAME})*/{MARKDOWN}",
         rf"doc/experiment(?:/{NAME})?/{MARKDOWN}",
         rf"doc/code/{NAME}/(?:Makefile|make\.bat|requirements\.txt)",
         rf"doc/code/{NAME}/source(?:/[^/]+)*/[^/]+"),
    ),
    "scripts": Rules((rf"scripts(?:/{NAME})*",), (rf"scripts(?:/{NAME})*/(?:{SCRIPT}|{CONFIG}|README\.md)",)),
    "tests": Rules(
        (r"tests", rf"tests/(?:product|integration|fixtures)(?:/{NAME})*"),
        (r"tests/(?:test_[a-z][a-z0-9_]*\.py|conftest\.py|__init__\.py|README\.md)",
         rf"tests/(?:product|integration)(?:/{NAME})*/(?:test_{NAME}\.py|conftest\.py|__init__\.py|README\.md)",
         rf"tests/fixtures(?:/{NAME})*/{PAYLOAD}"),
    ),
    "assets": Rules(
        (rf"assets(?:/{NAME}){{0,2}}", rf"assets/{NAME}/{NAME}/(?:files(?:/{NAME})*|scripts(?:/{NAME})*)"),
        (r"assets/README\.md", rf"assets/{NAME}/{NAME}/README\.md",
         rf"assets/{NAME}/{NAME}/files(?:/{NAME})*/{RESOURCE}",
         rf"assets/{NAME}/{NAME}/scripts(?:/{NAME})*/{SCRIPT}"),
    ),
    "data": Rules((r"data", rf"data/{NAME}(?:/{PAYLOAD})*"),
                  (rf"data(?:/{NAME})?/README\.md", rf"data/{NAME}(?:/{PAYLOAD})+/{PAYLOAD}")),
    # The project owns the checkout location. Upstream owns names inside it.
    "third_party": Rules((r"third_party", rf"third_party/{PAYLOAD}(?:/[^/]+)*"),
                         (r"third_party/README\.md", rf"third_party/{PAYLOAD}(?:/[^/]+)*/[^/]+")),
    "tmp": Rules((r"tmp", rf"tmp/{NAME}(?:/{PAYLOAD})*"), (rf"tmp/{NAME}(?:/{PAYLOAD})*/{PAYLOAD}",)),
}

EXPECTED = {
    "assets": "use assets/<Resource type>/<Resources>/README.md,files/ or scripts/",
    "conf": "use conf/config.<format> or conf/<Source Path Front Two Levels>/<Profile>",
    "data": "use data/<Data Set>/<Version>/ Save Data",
    "datasets": "use datasets/<Data set or family>/<Optional members>/ Save Data Achieved",
    "doc": "Use a fixed description page, or code,knowledge,environment,experiment Organizational theme",
    "experiment": "use experiment/<Data Set>/<Optional Model>/<Tasks>/<Research use>/ Save Run",
    "models": "use models/<Family>/<Optional Series>/ Save model realization",
    "tasks": "use tasks/<Tasks>/<Optional subtasks>/ Save Research Calculator",
    "tests": "use tests/test_<Behaviour>.py or tests/ It’s... product,integration,fixtures Branch",
}


def experiment_rules(root):
    catalogs = {}
    for suffix in ("yaml", "yml", "json", "toml"):
        main_config = root / f"conf/config.{suffix}"
        if main_config.is_file():
            text = main_config.read_text(encoding="utf-8")
            try:
                config = tomllib.loads(text) if suffix == "toml" else yaml.safe_load(text)
            except (ValueError, yaml.YAMLError):
                break
            if isinstance(config, dict) and isinstance(config.get("catalogs"), dict):
                catalogs = config["catalogs"]
            break

    def choices(role, nested):
        directory = root / COMPONENTS[role]
        names = set()
        pattern = NAME if nested else PLAIN_NAME
        entries = catalogs.get(role, {})
        if isinstance(entries, dict):
            names.update(name for name in entries if isinstance(name, str) and re.fullmatch(pattern, name))
        if directory.is_dir():
            for child in directory.iterdir():
                if child.is_dir() and re.fullmatch(pattern, child.name):
                    names.add(child.name)
                    if nested:
                        names.update(
                            f"{child.name}/{member.name}" for member in child.iterdir()
                            if member.is_dir() and re.fullmatch(NAME, member.name)
                        )
        return names

    directories = {"experiment"}
    files = {r"experiment/README\.md"}

    def alternatives(values):
        return "(?:" + "|".join(re.escape(value) for value in sorted(values)) + ")"

    datasets = choices("dataset", True)
    models = choices("model", True)
    tasks = choices("task", False)
    if not datasets:
        return Rules(tuple(directories), tuple(files))
    for dataset in datasets:
        directories.add(f"experiment/{dataset.split('/')[0]}")
    input_path = f"experiment/{alternatives(datasets)}"
    directories.add(input_path)
    model_paths = [input_path]
    if models:
        directories.add(f"{input_path}/{alternatives({name.split('/')[0] for name in models})}")
        model_paths.append(f"{input_path}/{alternatives(models)}")
    for prefix in model_paths:
        directories.add(prefix)
        if not tasks:
            continue
        task = f"{prefix}/{alternatives(tasks)}"
        study = rf"{task}/{PURPOSE}"
        role = rf"{study}(?:/(?!(?:artifacts|logs|reports|metadata|tmp|executions)(?:/|$)){PURPOSE})?"
        execution = rf"{role}/(?:executions/)?{EXECUTION}"
        run = rf"(?:{role}|{execution})"
        output = rf"{run}/(?:artifacts|logs|reports|metadata|tmp)"
        directories.update((task, study, role, rf"{role}/executions", execution, output,
                            rf"{output}(?:/{PAYLOAD})+"))
        files.update((rf"{run}/(?:README\.md|recipe\.toml|config\.(?:yaml|yml|toml|json)|manifest\.json)",
                      rf"{output}(?:/{PAYLOAD})*/{PAYLOAD}"))
    return Rules(tuple(directories), tuple(files))


def checkable_name(parts, is_directory):
    top = parts[0]
    if len(parts) >= 4 and parts[:2] == ["doc", "code"] and parts[3] in {
        "source", "Makefile", "make.bat", "requirements.txt",
    }:
        return False
    if len(parts) == 1 or top in {"third_party", "tmp"}:
        return False
    if top == "assets" and len(parts) > 3:
        return parts[3] == "scripts" and len(parts) > 4
    if top == "data" or parts[:2] == ["tests", "fixtures"]:
        return is_directory and (top != "data" or len(parts) <= 3)
    if top == "experiment":
        return (is_directory and len(parts) >= 2
                and not any(part in {"artifacts", "reports", "logs", "metadata", "tmp", "executions"}
                            or re.fullmatch(EXECUTION, part) for part in parts[1:]))
    return True


def check_layout(root):
    """Return concrete path failures for an absolute or relative project root."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"The project path should be a directory:{root}")
    configuration_owners = {"base", "scripts", *COMPONENTS.values()}
    rules = dict(RULES)
    if (root / "experiment").is_dir():
        rules["experiment"] = experiment_rules(root)
    violations = []
    inspected = 0

    def fail(path, rule, expected):
        violations.append({"path": path, "rule": rule, "expected": expected})

    if not project_name_valid(root.name):
        fail(".", "project_name", "Project root name with two or three words PascalCase,It’s full English words, named for engineering purposes.")

    def visit(directory, parent=""):
        nonlocal inspected
        config_files = []
        for entry in directory.iterdir():
            if entry.name.startswith(".") or entry.name == "__pycache__":
                continue
            relative = f"{parent}/{entry.name}" if parent else entry.name
            top = relative.split("/", 1)[0]
            is_directory = entry.is_dir()
            inspected += 1
            if not parent and not is_directory:
                if not re.fullmatch(ROOT_FILES, entry.name):
                    fail(relative, "root_file", "Root directory maintains open access, project description and build statement")
                continue
            selected = rules.get(top)
            if not selected or not selected.matches(relative, is_directory):
                rule = "root_directory" if not parent and is_directory else top
                expected = (
                    "Level-I catalogues must be assigned to the norm, with the main package and the common operational code being integrated base/"
                    if rule == "root_directory"
                    else EXPECTED.get(top, f"Press {top}/ Responsibilities, tiers and document titles")
                )
                fail(relative, rule, expected)
                continue
            parts = relative.split("/")
            fixed_file = (not is_directory and (entry.name == "config.py" or is_configuration_file(entry)
                                                or relative == "doc/conf.md"))
            if checkable_name(parts, is_directory) and not fixed_file:
                component = top in {"datasets", "models", "data"} and len(parts) <= 3
                component_config = top == "conf" and parts[1] in {"datasets", "models"}
                allow_digits = top == "experiment" or (
                    is_directory and (component or component_config)
                ) or (top in {"datasets", "models"} and entry.stem in parts[1:-1])
                for rule, expected in path_name_violations(entry, is_directory, allow_digits=allow_digits):
                    fail(relative, rule, expected)
            if top == "conf":
                if is_directory and parent:
                    owner_name = relative.removeprefix("conf/")
                    if (owner_name.split("/")[0] not in configuration_owners
                            or not (root / owner_name).is_dir()):
                        fail(relative, "configuration_owner", f"Exists responsible source directory {owner_name}")
                elif not is_directory:
                    if parent == "conf" and entry.stem != "config":
                        fail(relative, "configuration_root", "Unify Entry As conf/config.<format>")
                    config_files.append(relative)
            if is_directory and not entry.is_symlink():
                visit(entry, relative)
        if len(config_files) > 1:
            for path in config_files:
                fail(path, "configuration_branch", "Keep a file for each configuration branch")
        if re.fullmatch(rf"assets/{NAME}/{NAME}", parent) and not (directory / "README.md").is_file():
            fail(f"{parent}/README.md", "asset_description", "Recording of the use, source and related scripts of known resources")

    visit(root)
    violations.sort(key=lambda item: (item["path"], item["rule"]))
    return {"project": str(root), "passed": not violations, "checked": inspected, "violations": violations}
