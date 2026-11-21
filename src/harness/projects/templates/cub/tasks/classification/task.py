"""Purpose: Task execution interface to achieve universal access to classifications.

Scope of application: Classification task registration, parameter checking and operation. operation.py.
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
            raise ValueError("It takes at least two samples to compare performance.")
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
