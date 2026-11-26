"""Compatibility entry for tasks.evaluation.base_eval."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.evaluation.base_eval", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.evaluation import base_eval

    sys.modules[__name__] = base_eval
