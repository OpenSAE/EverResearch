"""Compatibility entry for tasks.inference.engine."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.inference.engine", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.inference import engine

    sys.modules[__name__] = engine
