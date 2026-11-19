"""分发本机文件处理和环境采集工具。

用于显式指定压缩包、传输路径或环境快照的工具调用。
"""

import sys


def main(argv):
    if not argv or argv == ["--help"]:
        print("用法：rh utils {archive,transfer,probe,compare} --help")
        return 0
    command, *args = argv
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
        print(f"找不到工具：{command}", file=sys.stderr)
        return 2
    try:
        return Engine().main(argv=args)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
