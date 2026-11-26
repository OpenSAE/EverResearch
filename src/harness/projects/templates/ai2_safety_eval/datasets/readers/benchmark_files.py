"""Resolve the original benchmark inputs bundled with the evaluation suite."""

from evaluation.configuration import package_directory


def benchmark_file(mode, task, *parts):
    return package_directory("ai2_safety_benchmark_inputs").joinpath(mode, task, *parts)
