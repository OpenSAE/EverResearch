"""目的：将分类实现接入统一的任务执行接口。

适用范围：分类任务登记、参数检查和运行。计算归 operation.py。
"""

from torch.utils.data import Subset

from ...contracts import EvaluationResult, PerformanceWorkload, TaskModule
from . import operation


class ClassificationTask(TaskModule):
    def validate_cfg(self, cfg, action):
        operation.validate_config(cfg, action)

    def validate_components(self, dataset, model):
        operation.validate_components(dataset, model)

    def check(self, request):
        return operation.precheck(
            request.build_model(),
            request.inputs.train,
            request.inputs.fixed_train,
            request.device,
            request.config,
        )

    def performance_workload(self, request):
        count = min(len(request.inputs.fixed_train), request.config["benchmark"]["samples"])
        if count < 2:
            raise ValueError("性能比较至少需要两个样本")
        data = Subset(request.inputs.fixed_train, range(count))
        model = request.build_model()
        model.eval()
        return PerformanceWorkload(
            samples=count,
            scope="fixed training images / evaluation transforms / forward",
            make_batches=lambda workers: operation.loader(data, request.config, workers),
            forward=lambda batch: operation.step(model, batch, request.device)[0],
        )

    def run(self, request):
        evaluation = operation.train_model(
            request.record,
            request.build_model(),
            request.inputs.train,
            request.inputs.test,
            request.device,
            request.config,
        )
        return EvaluationResult(summary=evaluation)
