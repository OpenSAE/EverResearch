"""Compatibility entry for tasks.fine_tuning.supervised."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.fine_tuning.supervised", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.fine_tuning import supervised

    sys.modules[__name__] = supervised
