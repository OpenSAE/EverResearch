"""Purpose: Provide independent precheck missions and record the results of actual inspections.

Scope of application: Visible precheck, performance comparison and automated precheck of official assignments.
"""

from ...contracts import EvaluationResult, TaskModule
from .performance import compare
from .timing import timed


class PrecheckTask(TaskModule):
    def validate_cfg(self, cfg, operation):
        if operation == "benchmark":
            for key, minimum in (("samples", 2), ("warmup", 0), ("repeats", 2)):
                value = cfg["benchmark"][key]
                if type(value) is not int or value < minimum:
                    raise ValueError(f"benchmark.{key} It must be at least. {minimum} Integer number")
            fraction = cfg["benchmark"].get("max_cuda_memory_fraction", 0.9)
            if type(fraction) not in {int, float} or not 0 < fraction <= 1:
                raise ValueError("benchmark.max_cuda_memory_fraction It must be. (0, 1] Internal")
            return
        samples = cfg["precheck"]["samples"]
        if type(samples) is not int or samples < 2:
            raise ValueError("precheck.samples It must be at least. 2 Integer number")

    def run(self, request):
        role = "performance" if request.action == "benchmark" else "precheck"
        if role == "performance":
            report = compare(request)
        else:
            timing = {}
            with timed(timing, "probe_total", request.device):
                report = request.target.check(request)
            report["timing_seconds"] = timing
        request.record.report(role, report)
        return EvaluationResult(summary={"target": request.target_name, "report": role})
