"""提供项目接入、本机资源绑定、结构成果审阅和独立工具的命令行入口。

用于显式选择项目及工作区的本机操作。
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
    stream = sys.stdout if not arguments or arguments == ["--help"] else sys.stderr
    print("用法：rh projects --help | rh utils --help", file=stream)
    return 0 if stream is sys.stdout else 2


if __name__ == "__main__":
    raise SystemExit(main())
