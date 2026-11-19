"""目的：让项目的正常操作沿同一入口选择组件、检查相容性和保存结果。

适用范围：分类模板的预检、性能比较和训练。任务拥有具体计算。
"""

import sys
from dataclasses import dataclass
from time import perf_counter

import torch

from ..contracts import EvaluationResult
from ..registry import resolve
from ..tasks.precheck.gate import automatic_precheck
from . import config, records
from .environment import snapshot


@dataclass(frozen=True)
class TaskRequest:
    config: dict
    record: records.Run
    inputs: object
    build_model: object
    device: torch.device
    action: str
    target_name: str
    target: object
    candidate_workers: int | None


def execute(operation, path, subname, *, data_root=None, candidate_workers=None, overrides=()):
    started = perf_counter()
    stage = "configuration"
    run = None
    cfg = None
    try:
        cfg = config.load(path, overrides)
        cfg["subname"] = subname
        if operation == "benchmark":
            benchmark = cfg["benchmark"]
            if candidate_workers is not None:
                benchmark["candidate_workers"] = candidate_workers
            candidate_workers = benchmark.get("candidate_workers")
        if operation in {"precheck", "benchmark"} and cfg["task"]["name"] != "precheck":
            cfg["task"] = {"name": "precheck", "target": cfg["task"]["name"]}
        task_name = cfg["task"]["name"]
        target_name = (
            cfg["task"].get("target", "classification") if task_name == "precheck" else task_name
        )
        action = (
            ("benchmark" if operation == "benchmark" else "precheck")
            if task_name == "precheck"
            else "train"
        )
        names = (cfg["dataset"]["name"], cfg["model"]["name"], task_name)
        dataset = resolve("dataset", names[0])
        model_builder = resolve("model", names[1])
        task = resolve("task", task_name)()
        if target_name == "precheck":
            raise ValueError("预检需要指定实际任务")
        target = resolve("task", target_name)() if task_name == "precheck" else task
        run = records.Run(operation, path, subname, components=names)
        print(run.root, flush=True)
        run.manifest["configuration"] = cfg
        config.resolve_data_root(
            cfg["dataset"], path, data_root, requires_root=dataset.REQUIRES_ROOT
        )
        dataset.validate_config(cfg["dataset"])
        cfg["model"] = model_builder.resolve_config(cfg["model"])
        task.validate_cfg(cfg, action)
        if target is not task:
            target.validate_cfg(cfg, action)
        if target_name not in dataset.SUPPORTED_TASKS:
            raise ValueError(f"数据集 {names[0]} 不支持任务 {target_name}")
        target.validate_components(dataset, model_builder)
        if action == "train":
            resolve("task", "precheck")().validate_cfg(cfg, "precheck")
            target.validate_cfg(cfg, "precheck")
        stage = "environment"
        device = config.prepare(cfg)
        run.manifest["environment"] = snapshot(device)
        run.record_configuration(cfg)
        stage = "inputs"
        inputs = dataset.load(cfg["dataset"], cfg["training"]["seed"])
        if inputs.classes != dataset.CLASSES:
            raise ValueError("数据实际类别与组件声明不一致")
        run.manifest["inputs"] = inputs.identity
        run.manifest["setup_seconds"] = perf_counter() - started
        run.save()

        def build_model():
            return model_builder.build(cfg["model"]).to(device)

        request = TaskRequest(
            cfg,
            run,
            inputs,
            build_model,
            device,
            action,
            target_name,
            target,
            candidate_workers,
        )
        if action == "train":
            stage = "automatic_precheck"
            automatic_precheck(request)
        stage = action
        result = task.run(request)
        if not isinstance(result, EvaluationResult):
            raise TypeError(f"{task_name} 必须返回 EvaluationResult")
        run.manifest["result"] = result.summary
        run.save("succeeded")
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, KeyboardInterrupt) as exc:
        if run is None:
            try:
                run = records.Run(operation, path, subname)
            except (OSError, ValueError) as location_error:
                print(f"experiment: {location_error}", file=sys.stderr)
                return 1
            run.manifest["configuration"] = cfg
            print(run.root, flush=True)
        missing_data = stage == "inputs" and isinstance(exc, FileNotFoundError)
        missing_cuda = (
            stage == "environment"
            and cfg["runtime"]["device"] == "cuda"
            and not (torch.cuda.is_available())
        )
        diagnostic = {"stage": stage, "type": type(exc).__name__, "message": str(exc)}
        if missing_data:
            diagnostic["next_action"] = "提供所选数据集需要的本地文件，再运行预检"
        elif missing_cuda:
            diagnostic["next_action"] = "选择可用的 CUDA 环境或将运行设备设为 CPU"
        if cfg is not None and "effective_config" not in run.manifest:
            run.record_configuration(cfg)
        run.manifest["diagnostics"].append(diagnostic)
        status = "blocked" if missing_data or missing_cuda else "failed"
        if isinstance(exc, KeyboardInterrupt):
            status = "partial"
        run.save(status)
        print(f"{stage}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 130 if isinstance(exc, KeyboardInterrupt) else 1
