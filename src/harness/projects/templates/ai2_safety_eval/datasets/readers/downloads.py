"""Cache benchmark downloads outside the installed evaluation package."""

import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlopen


def benchmark_directory(name):
    configured = os.environ.get("AI2_SAFETY_EVAL_DATA")
    default = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "ai2_safety_eval"
    path = Path(configured).expanduser() if configured else default
    return path / name


def download_benchmark_file(benchmark, filename, url):
    target = benchmark_directory(benchmark) / filename
    if target.is_file() and target.stat().st_size:
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        pending = Path(stream.name)
        try:
            with urlopen(url, timeout=30) as response:
                shutil.copyfileobj(response, stream)
            stream.flush()
            pending.replace(target)
        finally:
            pending.unlink(missing_ok=True)
    return target
