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
    stream = sys.stdout if not arguments or arguments == ["--help"] else sys.stderr
    print("Usage: rh {projects,utils,doctor,guide,skills,mcp} --help", file=stream)
    return 0 if stream is sys.stdout else 2


if __name__ == "__main__":
    raise SystemExit(main())
