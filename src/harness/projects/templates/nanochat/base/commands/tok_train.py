"""Compatibility entry for tasks.tokenization.train."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.tokenization.train", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.tokenization import train

    sys.modules[__name__] = train
