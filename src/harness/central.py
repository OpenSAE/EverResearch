"""Position central workspace, connect registered items and save the current source path.

For project access, resource selection and structural results search. Path binding is stored in the machine working area..
"""

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from io import BytesIO
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from platformdirs import user_cache_path, user_data_path, user_state_path

from .core.workspace import save, update_lock


class ProjectError(ValueError):
    """The project, resources or in-house registration is not operational."""


def identity(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", value):
        raise ProjectError(f"Invalid item or resource identifier:{value!r}")
    return value


@dataclass(frozen=True)
class HarnessContext:
    root: Path
    state: Path | None = None

    @property
    def workspace(self) -> Path:
        return self.root.parent if self.state is None else self.state

    @property
    def state_root(self) -> Path:
        return self.root if self.state is None else self.state

    @property
    def data_root(self) -> Path:
        override = os.environ.get("RH_DATA_ROOT")
        if override:
            return Path(override).expanduser().absolute()
        if self.state is None:
            return self.workspace / "data"
        return app_directory(user_data_path) / "data"

    def store_path(self, path: Path) -> str:
        workspace = self.workspace
        if path.is_relative_to(workspace):
            return path.relative_to(workspace).as_posix()
        return str(path)

    def bound_path(self, value: str) -> Path:
        path = Path(value).expanduser()
        if path.is_absolute():
            return path
        if ".." in path.parts:
            raise ProjectError(f"Relative bind paths beyond workspace:{value}")
        return self.workspace / path

    def resolve(self, relative: str, *, exists: bool = False) -> Path:
        requested = Path(relative)
        writable = requested.parts[:1] == (".workspace",) or requested.parts[:2] == ("src", "project")
        base = self.state_root if writable else self.root
        path = (base / requested).resolve()
        if requested.is_absolute() or ".." in requested.parts or not path.is_relative_to(base):
            raise ProjectError(f"The path goes beyond the central working area.:{relative}")
        if exists and not path.exists():
            raise ProjectError(f"Central file not found:{relative}")
        return path

    def bindings(self) -> dict:
        path = self.resolve(".workspace/harness/core/central/project_roots.json")
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def project_root(self, project_id: str) -> Path:
        raw = self.bindings().get(identity(project_id))
        if raw is None:
            raise ProjectError(f"Project has not bound the path of the machine:{project_id}")
        return self.source_directory(self.bound_path(raw))

    def project_record(self, project_id: str, filename: str | None = None) -> Path:
        """Locate the local record, including an existing record from the old layout."""
        name = identity(project_id)
        current = self.resolve(f"src/project/maintained/{name}")
        if not current.exists() and name != "maintained":
            legacy = self.resolve(f"src/project/{name}")
            if legacy.is_dir():
                current = legacy
        if filename is None:
            return current
        return self.resolve((current / filename).relative_to(self.state_root).as_posix())

    def source_directory(self, value: str | Path) -> Path:
        path = Path(value).expanduser().resolve(strict=True)
        if not path.is_dir() or path == self.root:
            raise ProjectError(f"The project path should point to a separate source directory:{path}")
        return path

    def register(self, project_id: str, source: str, *, replace=True) -> Path:
        project_id = identity(project_id)
        path = self.source_directory(source)
        target = self.resolve(".workspace/harness/core/central/project_roots.json")
        with update_lock(target):
            bindings = self.bindings()
            if (not replace and project_id in bindings
                    and self.bound_path(bindings[project_id]).resolve() != path):
                raise ProjectError(f"Project name {project_id!r} was registered at a different path.")
            for name, bound in bindings.items():
                if name != project_id and self.bound_path(bound).resolve() == path:
                    raise ProjectError(f"This directory has been bound to the item. {name}")
            bindings[project_id] = self.store_path(path)
            save(target, bindings, source=__file__)
        return path


def load_harness(root: str | Path | None = None) -> HarnessContext:
    if root is None:
        checkout = Path(__file__).resolve().parents[2]
        if not (checkout / ".agents/skills").is_dir():
            state = Path(os.environ.get("RH_STATE_DIR") or app_directory(user_state_path))
            return HarnessContext(installed_resources(), state.expanduser().resolve())
        root = checkout
    context = HarnessContext(Path(root).expanduser().resolve(strict=True))
    context.resolve(".agents/skills", exists=True)
    return context


def installed_resources() -> Path:
    """Materialize versioned resources so tools and agents can open real file paths."""
    archive = files("harness").joinpath("public_resources.zip")
    if not archive.is_file():
        raise ProjectError("EverResearch resources are missing from this installation. Reinstall EverResearch or supply --harness-root pointing to its source directory.")
    content = archive.read_bytes()
    cache = app_directory(user_cache_path).resolve()
    root = cache / ("resources-" + sha256(content).hexdigest())
    if root.is_dir():
        return root
    with update_lock(root):
        if not root.is_dir():
            with TemporaryDirectory(dir=cache) as temporary:
                destination = Path(temporary) / "resources"
                with ZipFile(BytesIO(content)) as bundle:
                    bundle.extractall(destination)
                destination.replace(root)
    return root
def app_directory(path_for):
    """Give new installations the EverResearch path and retain existing local state."""
    current = path_for("ever-research")
    legacy = path_for("researchharness")
    return legacy if not current.exists() and legacy.exists() else current
