"""Distribution of machine document processing and environmental collection tool.

Tool to call for visible specification of compression packages, transfer paths or environment snapshots.
"""

import sys


def main(argv):
    if not argv or argv == ["--help"]:
        print("Usage: rh utils {archive,transfer,probe,compare,release} --help")
        return 0
    command, *args = argv
    if command == "release":
        from .release import main as release_main

        return release_main(args)
    if command == "archive":
        from .transfer import module_main
        from .transfer.archive import Engine

        return module_main(Engine, args)
    if command == "transfer":
        from .transfer import module_main
        from .transfer.b2 import Engine

        return module_main(Engine, args)
    if command == "probe":
        from .probe import Engine
    elif command == "compare":
        from .compare import Engine
    else:
        print(f"No tool found:{command}", file=sys.stderr)
        return 2
    try:
        return Engine().main(argv=args)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
