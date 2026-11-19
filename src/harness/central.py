"""定位中央工作区、连接已登记项目并保存本机源码路径。

用于项目接入、资源选择与结构成果查找。路径绑定存放在本机工作区。
"""

from dataclasses import dataclass
import json
from pathlib import Path
import re

from .core.workspace import save, update_lock


WORKSPACE_MARKER = ".researchharness-workspace.json"


class ProjectError(ValueError):
    """项目、资源或本机登记无法使用。"""


def identity(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", value):
        raise ProjectError(f"无效的项目或资源标识：{value!r}")
    return value


def workspace_harness(directory: Path) -> Path | None:
    marker = directory / WORKSPACE_MARKER
    if marker.is_symlink():
        raise ProjectError(f"工作区标识应为普通文件：{marker}")
    if not marker.exists():
        return None
    entry = json.loads(marker.read_text())
    name = entry.get("harness") if isinstance(entry, dict) else None
    if (
        not isinstance(name, str)
        or Path(name).is_absolute()
        or Path(name).parts != (name,)
        or name in {".", ".."}
    ):
        raise ProjectError(f"工作区标识应声明一级 ResearchHarness 目录：{marker}")
    return directory / name


def find_harness() -> Path:
    current = Path.cwd().resolve()
    for directory in (current, *current.parents):
        candidate = workspace_harness(directory)
        if candidate is not None:
            return candidate
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / ".agents/skills").is_dir():
        return checkout
    raise ProjectError("找不到 ResearchHarness 工作区。请使用 --harness-root 指定源码目录")


@dataclass(frozen=True)
class HarnessContext:
    root: Path

    @property
    def workspace(self) -> Path | None:
        parent = self.root.parent
        return parent if workspace_harness(parent) == self.root else None

    def init_workspace(self) -> Path:
        workspace = self.root.parent
        marker = workspace / WORKSPACE_MARKER
        data = workspace / "data"
        if data == self.root:
            raise ProjectError("ResearchHarness 源码目录和共享 data/ 应分别占用一级目录")
        with update_lock(marker):
            existing = workspace_harness(workspace)
            if existing is not None and existing != self.root:
                raise ProjectError(f"工作区已使用另一份 ResearchHarness：{existing}")
            data.mkdir(exist_ok=True)
            if existing is None:
                save(marker, {"harness": self.root.name}, source=__file__)
        return workspace

    def store_path(self, path: Path) -> str:
        workspace = self.workspace
        if workspace is not None and path.is_relative_to(workspace):
            return path.relative_to(workspace).as_posix()
        return str(path)

    def bound_path(self, value: str) -> Path:
        path = Path(value).expanduser()
        if path.is_absolute():
            return path
        workspace = self.workspace
        if workspace is None or ".." in path.parts:
            raise ProjectError(f"相对绑定需要已初始化的工作区：{value}")
        return workspace / path

    def resolve(self, relative: str, *, exists: bool = False) -> Path:
        path = (self.root / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(self.root):
            raise ProjectError(f"路径超出中央工作区：{relative}")
        if exists and not path.exists():
            raise ProjectError(f"找不到中央文件：{relative}")
        return path

    def bindings(self) -> dict:
        path = self.resolve(".workspace/harness/core/central/project_roots.json")
        return json.loads(path.read_text()) if path.exists() else {}

    def project_root(self, project_id: str) -> Path:
        raw = self.bindings().get(identity(project_id))
        if raw is None:
            raise ProjectError(f"项目尚未绑定本机路径：{project_id}")
        return self.source_directory(self.bound_path(raw))

    def source_directory(self, value: str | Path) -> Path:
        path = Path(value).expanduser().resolve(strict=True)
        if not path.is_dir() or path == self.root:
            raise ProjectError(f"项目路径应指向独立的源码目录：{path}")
        return path

    def register(self, project_id: str, source: str) -> Path:
        project_id = identity(project_id)
        path = self.source_directory(source)
        target = self.resolve(".workspace/harness/core/central/project_roots.json")
        with update_lock(target):
            bindings = self.bindings()
            for name, bound in bindings.items():
                if name != project_id and self.bound_path(bound).resolve() == path:
                    raise ProjectError(f"这个目录已绑定到项目 {name}")
            bindings[project_id] = self.store_path(path)
            save(target, bindings, source=__file__)
        return path


def load_harness(root: str | Path) -> HarnessContext:
    context = HarnessContext(Path(root).expanduser().resolve(strict=True))
    context.resolve(".agents/skills", exists=True)
    return context
