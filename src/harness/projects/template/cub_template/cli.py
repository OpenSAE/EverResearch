"""目的：提供分类预检、同工作量性能比较、训练和运行清单读取。

适用范围：参考项目的正常命令行入口。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from .runtime.records import experiment_root, normalize_subname
from .runtime.runner import execute


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="operation", required=True)
    for name in ("run", "precheck", "benchmark", "train"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, help="默认从项目 conf/config.yaml 读取")
        command.add_argument("--subname", required=True, help="一至三个描述实验用途的词")
        command.add_argument("--data-root", type=Path)
        command.add_argument("--set", action="append", default=[], metavar="GROUP=VALUE")
        if name == "benchmark":
            command.add_argument(
                "--candidate-workers", type=int, help="与当前工作进程数比较的候选值"
            )
    inspect = commands.add_parser("inspect")
    inspect.add_argument("run_dir", type=Path)
    return result


def main(argv=None):
    commands = parser()
    args = commands.parse_args(argv)
    if args.operation == "inspect":
        try:
            path = args.run_dir / "metadata/manifest.json"
            print(json.dumps(json.loads(path.read_text()), ensure_ascii=False, indent=2))
            return 0
        except (OSError, ValueError) as exc:
            print(f"读取清单失败：{exc}", file=sys.stderr)
            return 1
    try:
        subname = normalize_subname(args.subname)
        config_path = args.config or experiment_root().parent / "conf/config.yaml"
    except ValueError as exc:
        commands.error(str(exc))
    return execute(
        args.operation,
        config_path,
        subname,
        data_root=args.data_root,
        candidate_workers=getattr(args, "candidate_workers", None),
        overrides=args.set,
    )
