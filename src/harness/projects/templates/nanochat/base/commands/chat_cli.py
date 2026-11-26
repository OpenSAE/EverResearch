"""Compatibility entry for tasks.inference.chat_cli."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("tasks.inference.chat_cli", run_name="__main__", alter_sys=True)
else:
    import sys
    from tasks.inference import chat_cli

    sys.modules[__name__] = chat_cli
