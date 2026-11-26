"""Compatibility entry for tasks.inference.benchmark."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.inference.benchmark", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.inference import benchmark

    sys.modules[__name__] = benchmark
