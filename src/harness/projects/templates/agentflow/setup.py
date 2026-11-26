"""Build AgentFlow and discover its tool packages in the current source tree."""

from pathlib import Path

from setuptools import find_packages, setup


PACKAGES = [
    "agentflow",
    "agentflow.agentflow",
    "agentflow.cli",
    "agentflow.instrumentation",
    "agentflow.tracer",
    "agentflow.utilities",
    "agentflow.engine",
    "agentflow.models",
    "agentflow.solver",
    "agentflow.tools",
    "agentflow.training",
    "agentflow.training_data",
    "agentflow.benchmark_data",
    "agentflow.verl",
    "agentflow.benchmarks",
    "agentflow.precheck",
]
TOOL_PACKAGES = find_packages(where="base/agent_flow/tools")

build_directory = Path(".build")
build_directory.mkdir(exist_ok=True)

setup(
    packages=PACKAGES + [f"agentflow.tools.{package}" for package in TOOL_PACKAGES],
    options={
        "build": {"build_base": str(build_directory)},
        "egg_info": {"egg_base": str(build_directory)},
    },
)
