"""提供 ResearchHarness 的工作区入口及项目错误类型。

用于中央项目接入与工具调用。
"""

from .central import HarnessContext, ProjectError, load_harness

__version__ = "0.2.0"
__all__ = ["HarnessContext", "ProjectError", "load_harness"]
