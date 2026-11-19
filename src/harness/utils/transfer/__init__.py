"""为独立传输与解压工具提供可选的本机项目标识。

用于直接处理显式路径，或在操作回执中附带已登记项目。
"""

import argparse
import sys


def module_main(engine_type, argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--harness-root")
    parser.add_argument("--project")
    args, remaining = parser.parse_known_args(argv)
    if bool(args.harness_root) != bool(args.project):
        parser.error("Provide --harness-root and --project together")
    if args.harness_root:
        from harness.central import load_harness

        try:
            load_harness(args.harness_root).project_root(args.project)
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    return engine_type(project_id=args.project).main(argv=remaining)
