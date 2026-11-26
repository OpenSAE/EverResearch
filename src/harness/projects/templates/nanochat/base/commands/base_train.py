"""Compatibility entry for tasks.base_training.train."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.base_training.train", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.base_training import train

    sys.modules[__name__] = train
