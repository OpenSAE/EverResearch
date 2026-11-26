"""Compatibility entry for tasks.fine_tuning.reinforcement."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.fine_tuning.reinforcement", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.fine_tuning import reinforcement

    sys.modules[__name__] = reinforcement
