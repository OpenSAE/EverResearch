"""Serve read-only ResearchHarness project checks through local MCP stdio.

Start one server for an explicitly selected project. The client can inspect that
project and read the shipped agreement without supplying arbitrary file paths.
"""

import argparse
from pathlib import Path

from .central import load_harness
from .core.experiment import check_experiment
from .core.layout import check_layout
from .core.project import check_project
from .distribution import GUIDES


def main(argv):
    parser = argparse.ArgumentParser(prog="rh mcp")
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        from mcp.server.fastmcp import FastMCP
    except ModuleNotFoundError as error:
        if error.name != "mcp":
            raise
        parser.exit(2, "Install ResearchHarness with its mcp extra to use this command.\n")
    context = load_harness()
    project = context.source_directory(args.project)
    server = FastMCP("ResearchHarness")

    @server.tool()
    def inspect_project() -> dict:
        """Inspect structural requirements of the configured research project."""
        return check_project(project)

    @server.tool()
    def inspect_layout() -> dict:
        """Check directory responsibilities and path naming in the configured project."""
        return check_layout(project)

    @server.tool()
    def inspect_experiment_records() -> dict:
        """Check existing run records and artifacts without launching an experiment."""
        return check_experiment(project)

    @server.tool()
    def read_project_agreement() -> str:
        """Read the shipped project layout, documentation, and execution rules."""
        return context.resolve(GUIDES["project-agreement"], exists=True).read_text(encoding="utf-8")

    server.run(transport="stdio")
    return 0
