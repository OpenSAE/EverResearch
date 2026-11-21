"""Position central workspace, connect registered items and save the current source path.

For project access, resource selection and structural results search. Path binding is stored in the machine working area..
"""

from dataclasses import dataclass
import json
from pathlib import Path
import re

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

    @property
    def workspace(self) -> Path:
        return self.root.parent

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
        path = (self.root / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(self.root):
            raise ProjectError(f"The path goes beyond the central working area.:{relative}")
        if exists and not path.exists():
            raise ProjectError(f"Central file not found:{relative}")
        return path

    def bindings(self) -> dict:
        path = self.resolve(".workspace/harness/core/central/project_roots.json")
        return json.loads(path.read_text()) if path.exists() else {}

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
        return self.resolve((current / filename).relative_to(self.root).as_posix())

    def source_directory(self, value: str | Path) -> Path:
        path = Path(value).expanduser().resolve(strict=True)
        if not path.is_dir() or path == self.root:
            raise ProjectError(f"The project path should point to a separate source directory:{path}")
        return path

    def register(self, project_id: str, source: str) -> Path:
        project_id = identity(project_id)
        path = self.source_directory(source)
        target = self.resolve(".workspace/harness/core/central/project_roots.json")
        with update_lock(target):
            bindings = self.bindings()
            for name, bound in bindings.items():
                if name != project_id and self.bound_path(bound).resolve() == path:
                    raise ProjectError(f"This directory has been bound to the item. {name}")
            bindings[project_id] = self.store_path(path)
            save(target, bindings, source=__file__)
        return path


def load_harness(root: str | Path | None = None) -> HarnessContext:
    if root is None:
        root = Path(__file__).resolve().parents[2]
        if not (root / ".agents/skills").is_dir():
            raise ProjectError("Please. --harness-root Assign ResearchHarness Source Directory")
    context = HarnessContext(Path(root).expanduser().resolve(strict=True))
    context.resolve(".agents/skills", exists=True)
    return context
