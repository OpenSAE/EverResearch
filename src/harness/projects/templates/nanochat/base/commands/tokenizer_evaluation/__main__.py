"""Compatibility entry for tasks.tokenization.evaluate."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.tokenization.evaluate", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.tokenization import evaluate

    sys.modules[__name__] = evaluate
