"""Distribution of machine document processing and environmental collection tool.

Tool to call for visible specification of compression packages, transfer paths or environment snapshots.
"""

import sys


def main(argv):
    if not argv or argv in (["--help"], ["-h"]):
        print("""EverResearch utilities

Usage: rh utils <command> [options]

  quick-demo  Preview project onboarding and reproduce a sample experiment.
  archive     Inspect an archive or extract selected files.
  transfer    Move files to or from supported storage.
  probe       Capture the current software and hardware environment.
  compare     Compare two environment snapshots.
  release     Build and verify the files used for distribution.

Use rh utils <command> --help for command options.""")
        return 0
    command, *args = argv
    if command == "quick-demo":
        from .quick_demo import main as quick_demo

        return quick_demo(args)
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
