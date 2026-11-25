"""Command entry for project access, binding of in-house resources, review of structural results and independent tools.

Local operation for visible selection of items and workspaces.
"""

import sys

from .projects.manage import main as projects_main


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments[:1] == ["projects"]:
        return projects_main(arguments[1:])
    if arguments[:1] == ["utils"]:
        from .utils import main as utils_main

        return utils_main(arguments[1:])
    if arguments and arguments[0] in {"doctor", "guide", "skills"}:
        from .distribution import main as distribution_main

        return distribution_main(arguments[0], arguments[1:])
    if arguments[:1] == ["mcp"]:
        from .mcp import main as mcp_main

        return mcp_main(arguments[1:])
    if not arguments or arguments in (["--help"], ["-h"]):
        print("""EverResearch — organize, check, and reproduce research projects.

Usage: rh <command> [options]

  projects  Preview onboarding, check layout, and manage project resources.
  utils     Run the sample project, transfer files, or build release packages.
  doctor    Verify the local installation and bundled resources.
  guide     Open the project agreement, example, or a shared skill.
  skills    Install or remove project-local agent skills.
  mcp       Serve read-only project checks over MCP.

Start with: rh projects project check <project-path>
Use rh <command> --help for command options.""")
        return 0
    print(f"Unknown rh command: {arguments[0]}. Run rh --help.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
