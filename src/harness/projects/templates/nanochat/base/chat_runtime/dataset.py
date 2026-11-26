"""Compatibility entry for nanochat.climbmix.dataset."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("nanochat.climbmix.dataset", run_name="__main__", alter_sys=True)
else:
    import sys
    from nanochat.climbmix import dataset

    sys.modules[__name__] = dataset
